from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import datetime

app = Flask(__name__)
CORS(app)

history = []
history_id_counter = 1

def safe_eval(expr):
    allowed_names = {
        "sqrt": math.sqrt,
        "pow": math.pow,
    }
    try:
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

@app.route('/api/calculate', methods=['POST'])
def calculate():
    global history_id_counter
    data = request.get_json()
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
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify({"history": history}), 200

@app.route('/api/history/<int:item_id>', methods=['DELETE'])
def delete_history_item(item_id):
    global history
    history = [item for item in history if item["id"] != item_id]
    return jsonify({"success": True}), 200

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    global history
    history = []
    return jsonify({"success": True}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
