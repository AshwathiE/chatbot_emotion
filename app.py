from flask import Flask, request, jsonify, send_from_directory
import os
import logging
from dotenv import load_dotenv
from groq import Groq


load_dotenv()
app = Flask(__name__, static_folder='static')

# Allow overriding model via environment variable for easy updates when models are deprecated
DEFAULT_GROQ_MODEL = os.environ.get('GROQ_MODEL', 'meta-llama/llama-4-scout-17b-16e-instruct')

# simple logging to help debug API errors
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def extract_topic(text):
    # Extract the first sentence or up to 30 chars as the topic
    topic = text.split('.\n')[0].split('. ')[0].split('\n')[0].strip()
    if not topic:
        topic = text[:30]
    if len(topic) > 30:
        topic = topic[:30] + '…'
    return topic

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    messages = data.get('messages', [])
    api_key = os.environ.get('GROQ_API_KEY') or request.headers.get('GROQ_API_KEY')
    if not api_key:
        return jsonify({'error': 'Missing Groq API key'}), 401
    client = Groq(api_key=api_key)
    # Only send the last 20 messages for context
    try:
        response = client.chat.completions.create(
            model=DEFAULT_GROQ_MODEL,
            messages=messages[-20:],
            temperature=0.2,
            top_p=0.95,
            max_tokens=1024
        )

        # Log raw response for debugging (repr to avoid serialization issues)
        logger.debug('Groq response repr: %s', repr(response))

        # Try a few common ways to extract the assistant text from the SDK response
        def _extract_content(resp):
            try:
                return resp.choices[0].message.content
            except Exception:
                pass
            try:
                return resp.choices[0].message['content']
            except Exception:
                pass
            try:
                return resp.choices[0].delta.content
            except Exception:
                pass
            try:
                return resp.choices[0].text
            except Exception:
                pass
            return None

        content = _extract_content(response)
        if content is None:
            logger.error('Could not extract content from Groq response: %s', repr(response))
            return jsonify({'error': 'Unexpected response format from Groq API'}), 502

        return jsonify({'response': content})

    except Exception as e:
        # Log the exception with stacktrace for debugging
        logger.exception('Error calling Groq API: %s', e)
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

@app.route('/topics', methods=['POST'])
def topics():
    data = request.get_json()
    messages = data.get('messages', [])
    topics = [extract_topic(m['content']) for m in messages if m.get('role') == 'user']
    return jsonify({'topics': topics})

if __name__ == '__main__':
    app.run(debug=True)
