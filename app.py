from flask import Flask, request, jsonify
import os
import google.generativeai as genai
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

try:
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        logging.info("AI online")
    else:
        model = None
except Exception as e:
    model = None
    logging.error(f"Error: {e}")

@app.route('/')
def index():
    return '''
    <h1>Kaisa AI Backend Running</h1>
    <p>Use POST /api/chat to send messages</p>
    <p>Status: ''' + ('AI Connected' if model else 'AI Disconnected') + '''</p>
    '''

@app.route('/api/chat', methods=['POST'])
def chat():
    if not model:
        return jsonify(error='AI not configured'), 503
    
    data = request.get_json()
    message = data.get('message')
    if not message:
        return jsonify(error='No message'), 400
    
    prompt = f"You are Kaisa AI, Sheikh Arsalan's revolutionary voice. Reply: {message}"
    
    try:
        response = model.generate_content(prompt)
        return jsonify(success=True, response=response.text)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
