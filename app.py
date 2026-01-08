# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from agent import ask_pandas_ai
import os

app = Flask(__name__)
CORS(app)

# Ensure chart directory exists so PandasAI doesn't crash
os.makedirs("static/charts", exist_ok=True)

@app.route('/api/ask', methods=['POST'])
def chat():
    data = request.json
    question = data.get('question', '')
    
    if not question:
        return jsonify({"error": "No question provided"}), 400

    print(f"🤖 User asked: {question}")
    result = ask_pandas_ai(question)
    print(f"💡 Response: {result}")
    
    return jsonify(result)

# Route to serve the generated chart images
@app.route('/charts/<path:filename>')
def serve_chart(filename):
    return send_from_directory('static/charts', filename)

if __name__ == '__main__':
    print("🚀 ARGOS Data Engine (PandasAI) running on http://localhost:5001")
    app.run(port=5001, debug=True)