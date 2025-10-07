from flask import Flask, request, jsonify
import os
import google.generativeai as genai
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Configure AI
try:
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        logging.info("Gemini AI is online")
    else:
        model = None
        logging.error("GEMINI_API_KEY not set")
except Exception as e:
    model = None
    logging.error(f"AI config error: {e}")

@app.route('/')
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
    
    prompt = f"You are Kaisa AI, Sheikh Arsalan's digital voice. Respond: {message}"
    
    try:
        response = model.generate_content(prompt)
        return jsonify(success=True, response=response.text)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
