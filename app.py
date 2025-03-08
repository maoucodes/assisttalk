from flask import Flask, request, jsonify, render_template, Response
import requests
from flask_cors import CORS
import time
from flask import stream_with_context
from Search.main import search
app = Flask(__name__)
CORS(app)


cookies = {
    'intercom-id-evnv2y8k': 'bb169723-f3fa-497a-9b9a-eff63e9f4a37',
    'intercom-device-id-evnv2y8k': '9ff5ba33-cb98-4a4b-bf73-b78e688428d8',
    'state-csrf': 'zjt84werzwtrisxtnr6wl',
    'together_auth_cookie': '%7B%22expires%22%3A%222026-02-19T13%3A13%3A42.351Z%22%2C%22session%22%3A%220ac5b52fe6056114a28ec92586afc401604d163a119987a79166f736d767c7ce23001119fdfd7110ab7730c5aa40d83a6a4b0fbd4210bf32003bbb3ec17b7465353cb8ff6d892b72ed7ef2ab41871e01e0bc6c5a9d08c0d8b236722cf7c513d5c26ccfed10e490abda57cde4c1b99ea3b0b5c37fed08317e929ac342729f7d9d%22%7D',
}

headers = {
    'accept': '*/*',
    'authorization': 'Bearer 4d900964e385651ea685af6f6cd5573a17b421f50657f73f903525177915a7e2',
    'content-type': 'application/json',
    'referer': 'https://api.together.ai/playground/chat/deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free',
    'user-agent': 'Mozilla/5.0',
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    messages = data.get('messages', [])
    model = data.get('model', 'meta-llama/Llama-Vision-Free')
    
    # Create a thread-local copy of messages
    current_messages = messages.copy()
    
    # Handle the case where the last message might be an array with text and image
    if messages and isinstance(messages[-1].get('content'), list):
        current_messages = messages
    else:
        current_messages.append({
            'content': [{
                'type': 'text',
                'text': user_input
            }],
            'role': 'user'
        })
    
    json_data = {
        'model': model,
        'max_tokens': None,
        'temperature': 0.7,
        'top_p': 0.7,
        'top_k': 50,
        'repetition_penalty': 1,
        'stream_tokens': True,
        'stop': ['<|eot_id|>', '<|eom_id|>'],
        'messages': current_messages,
        'stream': True,
    }
    
    def generate():
        max_retries = 5
        base_delay = 1  # Initial delay in seconds
        
        for attempt in range(max_retries):
            response = requests.post('https://api.together.ai/inference', cookies=cookies, headers=headers, json=json_data, stream=True)
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data: '):
                            yield f'{decoded_line}\n\n'
                return
            elif response.status_code == 429:
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    time.sleep(0.5)
                    continue
                yield 'data: {"error": "Rate limited, maximum retries reached"}\n\n'
                return
            else:
                yield f'data: {{"error": "Unexpected status code: {response.status_code}"}}\n\n'
                return
        
        yield 'data: {"error": "Maximum retries reached"}\n\n'
    
    return Response(generate(), mimetype='text/event-stream')
    
@app.route('/search', methods=['POST', 'GET'])
def search_google():
    query = request.args.get('query')
    result = search(query, advanced=True, num_results=5)
    print(result)
    return jsonify(result)