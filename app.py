from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import requests
import json
import time
from character import characters

app = Flask(__name__)
CORS(app)  #

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

@app.route('/chat')
def chat_page():
    return render_template('chat.html')

@app.route('/character-chat')
def character_chat_page():
    return render_template('character-chat.html')

@app.route('/get-characters')
def get_characters():
    return jsonify({
        id: {
            'name': char.name,
            'age': char.age,
            'gender': char.gender,
            'pronouns': char.pronouns,
            'occupation': char.occupation,
            'personality': char.personality,
            'background': char.background,
            'hobbies': char.hobbies,
            'strengths': char.strengths,
            'weaknesses': char.weaknesses,
            'speech_style': char.speech_style,
            'conversational_quirks': char.conversational_quirks,
            'knowledge_base': char.knowledge_base,
            'avatar_url': char.avatar_url
        } for id, char in characters.items()
    })

@app.route('/character-chat', methods=['POST'])
def character_chat():
    data = request.json
    character_id = data.get('character_id')
    user_message = data.get('message')
    chat_messages = data.get('messages', [])
    
    if character_id not in characters:
        return jsonify({'error': 'Character not found'}), 404
    
    character = characters[character_id]
    
    # Prepare messages for the API
    api_messages = [character.get_initial_message()]
    api_messages.append({
        'role': 'user',
        'content': user_message
    })
    for msg in chat_messages:
        api_messages.append({
            'role': msg['role'],
            'content': msg['content']
        })
    
    json_data = {
        'model': 'meta-llama/Llama-Vision-Free',
        'max_tokens': None,
        'temperature': 0.7,
        'top_p': 0.7,
        'top_k': 50,
        'repetition_penalty': 1,
        'stream_tokens': True,
        'stop': ['<|eot_id|>', '<|eom_id|>'],
        'messages': api_messages,
        'stream': True,
    }
    
    def generate():
        max_retries = 5
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = requests.post('https://api.together.ai/inference', cookies=cookies, headers=headers, json=json_data, stream=True)
                
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            if decoded_line.startswith('data: '):
                                try:
                                    response_data = json.loads(decoded_line[6:])
                                    if 'choices' in response_data and len(response_data['choices']) > 0:
                                        text = response_data['choices'][0].get('text', '')
                                        if text:
                                            yield f'data: {json.dumps({"text": text})}\n\n'
                                except json.JSONDecodeError:
                                    continue
                    return
                elif response.status_code == 429:
                    if attempt < max_retries - 1:
                        time.sleep(0.5)
                        continue
                    yield f'data: {json.dumps({"error": "Rate limited, maximum retries reached"})}\n\n'
                    return
                else:
                    yield f'data: {json.dumps({"error": f"Unexpected status code: {response.status_code}"})}\n\n'
                    return
            except Exception as e:
                yield f'data: {json.dumps({"error": f"An error occurred: {str(e)}"})}\n\n'
                return
        
        yield f'data: {json.dumps({"error": "Maximum retries reached"})}\n\n'
    
    return Response(generate(), mimetype='text/event-stream')

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Return the URL for the uploaded image
        image_url = f'/static/uploads/{filename}'
        return jsonify({'url': image_url})
    
    return jsonify({'error': 'Invalid file type'}), 400

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
    
    max_retries = 5
    base_delay = 1  # Initial delay in seconds
    
    for attempt in range(max_retries):
        response = requests.post('https://api.together.ai/inference', cookies=cookies, headers=headers, json=json_data, stream=True)
        
        if response.status_code == 200:
            assistant_response = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data: "):
                        try:
                            data = json.loads(decoded_line[6:])  # Remove "data: " prefix and parse JSON
                            if "choices" in data:
                                for choice in data["choices"]:
                                    assistant_response += choice["text"]
                        except json.JSONDecodeError:
                            continue
            messages.append({'content': assistant_response, 'role': 'assistant'})
            return jsonify({'messages': messages})
        elif response.status_code == 429:
            if attempt < max_retries - 1:  # Don't sleep on the last attempt
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                time.sleep(0.5)
                continue
            return jsonify({'error': 'Rate limited, maximum retries reached'}), 429
        else:
            return jsonify({'error': f'Unexpected status code: {response.status_code}'}), response.status_code
    
    return jsonify({'error': 'Maximum retries reached'}), 429
