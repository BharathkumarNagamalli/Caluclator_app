from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import math
import datetime
import os

app = Flask(__name__)
# Enable CORS for frontend communication
CORS(app)

# In-memory storage for calculation history
history = []
history_id_counter = 1

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
    Serve the calculator UI page.
    """
    return send_from_directory(os.path.dirname(__file__), 'ui.html')

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint for the backend.
    """
    return jsonify({"message": "Calculator Backend is running."}), 200

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """
    Endpoint to calculate a mathematical expression.
    Expects JSON: {"expression": "..."}
    """
    global history_id_counter
    data = request.get_json()
    
    # Request validation
    if not data or 'expression' not in data:
        return jsonify({"success": False, "error": "No expression provided"}), 400
    
    expr = data['expression']
    
    try:
        result = safe_eval(expr)
        
        # Add to history
        record = {
            "id": history_id_counter,
            "expression": expr,
            "result": result,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
        history.append(record)
        history_id_counter += 1
        
        return jsonify({
            "success": True,
            "result": result,
            "expression": expr
        }), 200
    except ValueError as e:
        # Exception handling for invalid expressions or math errors
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route('/api/history', methods=['GET'])
def get_history():
    """
    Endpoint to retrieve the calculation history.
    """
    return jsonify({"history": history}), 200

@app.route('/api/history/<int:item_id>', methods=['DELETE'])
def delete_history_item(item_id):
    """
    Endpoint to delete a specific item from the calculation history.
    """
    global history
    history = [item for item in history if item["id"] != item_id]
    return jsonify({"success": True}), 200

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """
    Endpoint to clear all calculation history.
    """
    global history
    history = []
    return jsonify({"success": True}), 200

if __name__ == '__main__':
    # Ensure the application runs on port 8080 or the PORT environment variable
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

