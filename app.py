from flask import Flask, request, jsonify, render_template, Response
import requests
from flask_cors import CORS
import time
from flask import stream_with_context
from Search.main import search
from explore.index import get_trending_news

app = Flask(__name__)

CORS(app)

cookies = {
    'intercom-id-evnv2y8k': 'fea4d452-f9be-42e0-93e3-1e47a3836362',
    'intercom-device-id-evnv2y8k': '2bb3e469-0159-4b6b-a33e-1aea4b51ccb1',
    '__stripe_mid': 'e0f7c1ba-56c6-44d4-ba1d-cf4611453eb43cf922',
    'state-csrf': '6f2o8nqgee2dfqdmhaxipe',
    'together_auth_cookie': '%7B%22expires%22%3A%222026-04-09T15%3A14%3A08.985Z%22%2C%22session%22%3A%220eae08c6fd1b79a22476a317d440a2104d74cd3ba333e40771b5ce50a90784297eb82eff36263debca2ee0658abe3e43cab97f87794421111d4bdec56b43dd2595ee22a165c123ba3d0f807759555b5f6d3f51b7c248e7cefcdf0f0b897f62b25b2a569e2cb89633032f15dca9818f39ed49f3ac2d7e0bc3d24517c62c78b1e4%22%7D',
    '__stripe_sid': '979e00a2-06ed-45be-9a95-88d7e7580f625ccce4',
    'intercom-session-evnv2y8k': 'TzZzSzBNRG8xdHJtTVprMm1zUXFob0M2ekhFV3VmeDZFcW5UVldlYmFYc3RsRjFmdWJidjU1ZXVSZzNOSW9QTE82OUx6anlvMWVncmlTd2ZvOERDUXN4OUdoSEM5ZzRnQmh4d2o5S3JKeDA9LS00S3JOclNpNzU0VkVBaTNRNWhSMm93PT0=--2719775e99e920753d35527a45a6731bac5e8f8f',
    'AMP_7112ee0414': 'JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjJmY2ZmNjE3Ny00Yzg0LTRlOTItYTFhMC1kM2Y1ZjllOTFkYTglMjIlMkMlMjJ1c2VySWQlMjIlM0ElMjI2N2I1ZDkwNDNkZTIyN2Q0OGIzMWEwZTMlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzQ0MjExNjQyMjEwJTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTc0NDIxMTc1ODAwOSUyQyUyMmxhc3RFdmVudElkJTIyJTNBMjMyJTJDJTIycGFnZUNvdW50ZXIlMjIlM0E1JTdE',
}

headers = {
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9,ja;q=0.8',
    'authorization': 'Bearer 4d900964e385651ea685af6f6cd5573a17b421f50657f73f903525177915a7e2',
    'content-type': 'application/json',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'x-stainless-arch': 'unknown',
    'x-stainless-lang': 'js',
    'x-stainless-os': 'Unknown',
    'x-stainless-package-version': '0.11.1',
    'x-stainless-retry-count': '0',
    'x-stainless-runtime': 'browser:chrome',
    'x-stainless-runtime-version': '135.0.0',
    'referer': 'https://api.together.ai/playground/v2/chat/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8',
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
    result = search(query, advanced=True, num_results=10)
    return jsonify(result)

@app.route('/search-images', methods=['POST', 'GET'])
def search_google_images():
    query = request.args.get('query')
    result = search(query, advanced=True, num_results=10)
    return jsonify(result)

@app.route('/suggestions', methods=['POST', 'GET'])
def get_suggestions():
    return get_trending_news()