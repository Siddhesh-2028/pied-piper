# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from agent import ask_pandas_ai

app = Flask(__name__)
CORS(app)

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

if __name__ == '__main__':
    print("🚀 ARGOS Data Engine (Text Only) running on http://localhost:5001")
    app.run(port=5001, debug=True)