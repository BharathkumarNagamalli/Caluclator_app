from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import math
import datetime
import os

app = Flask(__name__)
# Enable CORS for frontend communication
CORS(app)

# Database configuration
# Use DATABASE_URL from environment if available, otherwise fallback to local SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///calculator.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model for Calculation History
class CalculationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expression = db.Column(db.String(255), nullable=False)
    result = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        # Convert float to int if it's a whole number, to match frontend expectations
        res = self.result
        if res.is_integer():
            res = int(res)
        return {
            "id": self.id,
            "expression": self.expression,
            "result": res,
            "timestamp": self.timestamp
        }

# Create tables if they don't exist
with app.app_context():
    db.create_all()

def safe_eval(expr):
    """
    Safely evaluate a mathematical expression.
    Supports basic arithmetic (+, -, *, /) and math functions (sqrt, pow).
    """
    allowed_names = {
        "sqrt": math.sqrt,
        "pow": math.pow,
    }
    try:
        # Evaluate the expression without builtins for security
        result = eval(expr, {"__builtins__": {}}, allowed_names)
        if isinstance(result, (int, float)):
            # If the result is a float but has no decimal part, return as int
            if isinstance(result, float) and result.is_integer():
                return int(result)
            return round(result, 8)
        else:
            raise ValueError("Invalid result")
    except ZeroDivisionError:
        raise ValueError("Division by zero")
    except Exception:
        raise ValueError("Invalid expression")

@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint to verify the backend is running.
    """
    return jsonify({"message": "Calculator Backend is running."}), 200

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """
    Endpoint to calculate a mathematical expression.
    Expects JSON: {"expression": "..."}
    """
    data = request.get_json()
    
    # Request validation
    if not data or 'expression' not in data:
        return jsonify({"success": False, "error": "No expression provided"}), 400
    
    expr = data['expression']
    
    try:
        result = safe_eval(expr)
        
        # Add to database history
        record = CalculationHistory(
            expression=expr,
            result=float(result), # Store as float in DB
            timestamp=datetime.datetime.utcnow().isoformat() + "Z"
        )
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "result": result,
            "expression": expr
        }), 200
    except ValueError as e:
        # Exception handling for invalid expressions or math errors
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Database error occurred"
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """
    Endpoint to retrieve the calculation history.
    """
    try:
        records = CalculationHistory.query.all()
        history = [record.to_dict() for record in records]
        return jsonify({"history": history}), 200
    except Exception as e:
        return jsonify({"success": False, "error": "Database error occurred"}), 500

@app.route('/api/history/<int:item_id>', methods=['DELETE'])
def delete_history_item(item_id):
    """
    Endpoint to delete a specific item from the calculation history.
    """
    try:
        record = CalculationHistory.query.get(item_id)
        if record:
            db.session.delete(record)
            db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Database error occurred"}), 500

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """
    Endpoint to clear all calculation history.
    """
    try:
        db.session.query(CalculationHistory).delete()
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Database error occurred"}), 500

if __name__ == '__main__':
    # Ensure the application runs on port 8080 or the PORT environment variable
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
