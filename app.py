from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import google.generativeai as genai
import logging
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Configure AI
try:
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        logging.info("Gemini AI online")
    else:
        model = None
except Exception as e:
    model = None
    logging.error(f"AI error: {e}")

# Memory storage (simple in-memory for now)
conversation_history = []
personality_context = """
You are Kaisa AI, the digital voice of Sheikh Arsalan Ullah Chishti.
Identity: Queer Bahujan politician, activist, tech founder.
Mission: Caste abolition, trans justice, anti-Islamophobia, youth power.
Style: Revolutionary, sharp, poetic, no-bullshit. Speak like you're leading a movement.
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify(status='online', ai='connected' if model else 'disconnected')

@app.route('/api/chat', methods=['POST'])
def chat():
    if not model:
        return jsonify(error='AI not configured'), 503
    
    data = request.get_json()
    message = data.get('message')
    if not message:
        return jsonify(error='No message'), 400
    
    # Build context from memory
    context = personality_context + "\n\nRecent conversation:\n"
    for msg in conversation_history[-5:]:  # Last 5 messages
        context += f"{msg['role']}: {msg['content']}\n"
    
    prompt = f"{context}\n\nUser: {message}\nKaisa AI:"
    
    try:
        response = model.generate_content(prompt)
        reply = response.text
        
        # Store in memory
        conversation_history.append({'role': 'User', 'content': message, 'time': datetime.now().isoformat()})
        conversation_history.append({'role': 'Kaisa AI', 'content': reply, 'time': datetime.now().isoformat()})
        
        return jsonify(success=True, response=reply)
    except Exception as e:
        logging.error(f"Chat error: {e}")
        return jsonify(success=False, error=str(e)), 500

@app.route('/api/memory', methods=['GET'])
def get_memory():
    return jsonify(history=conversation_history)

@app.route('/api/memory/clear', methods=['POST'])
def clear_memory():
    conversation_history.clear()
    return jsonify(success=True, message='Memory cleared')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
