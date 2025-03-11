from flask import Flask, request, jsonify, render_template, Response
import requests
from flask_cors import CORS
import time
from flask import stream_with_context
from Search.main import search

app = Flask(__name__)

CORS(app)


cookies = {
    'intercom-id-evnv2y8k': 'fea4d452-f9be-42e0-93e3-1e47a3836362',
    'intercom-device-id-evnv2y8k': '2bb3e469-0159-4b6b-a33e-1aea4b51ccb1',
    '__stripe_mid': 'e0f7c1ba-56c6-44d4-ba1d-cf4611453eb43cf922',
    'state-csrf': 'z4pfq6gvoqmg92gkq6bljm',
    'together_auth_cookie': '%7B%22expires%22%3A%222026-03-11T14%3A02%3A04.928Z%22%2C%22session%22%3A%22b672ad1b7784bcbb96a5b43058d3d4fbd8327f32dd020f12664307eed353c1b86f1e0d515a4c8b2d990dc5017ed1f13cd7514dee6263bcbd9e03446143245ba0c21968f273967cdb73dd6fedb0a9ff2b65a3ed2ce66b2cd4f94053c747be019d93327fa1f6b24bca9a559ba98ec48f2b51c3be242891d86bb670453120eed64e%22%7D',
    'AMP_MKTG_7112ee0414': 'JTdCJTIycmVmZXJyZXIlMjIlM0ElMjJodHRwcyUzQSUyRiUyRmFjY291bnRzLmdvb2dsZS5jb20lMkYlMjIlMkMlMjJyZWZlcnJpbmdfZG9tYWluJTIyJTNBJTIyYWNjb3VudHMuZ29vZ2xlLmNvbSUyMiU3RA==',
    'intercom-session-evnv2y8k': 'UWtNaFEraEJ3ZzcydXlwUC94MHhPcGg3eGZ6RXJkM2c3a2J3R1dwUGR4RWRzQnozWFNLQ0tqbW5za0gvU3RodmNZNXh4NVhRL3I5RWhwNjZKRnd5M21XRm9sZUZhTm05ZUUvaXMxZEYrNjQ9LS1OS0dDcFpuZGRCRE5XaWkxcDVZOEtBPT0=--83289f02195d8a45658bb26d7036c1bf9cfe9887',
    '__stripe_sid': '7e7f0bab-efaa-4ec6-ae34-2857cccc4f644bc033',
    'AMP_7112ee0414': 'JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjI5NGU0MzFjOS02OTM0LTQwMGItYTk3Ni0yZjEyNzZmNjg4YzklMjIlMkMlMjJ1c2VySWQlMjIlM0ElMjI2N2I4M2E1Y2Q4MzFiZTcxYjAyYjM4MmElMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzQxNzAxNzE5MDE5JTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTc0MTcwMTc1NTU4MSUyQyUyMmxhc3RFdmVudElkJTIyJTNBODklMkMlMjJwYWdlQ291bnRlciUyMiUzQTQlN0Q=',
}

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,ja;q=0.8',
    'authorization': 'Bearer bb80c2632e2d0ee9c8b5208fcfca771159cf0fd8f9b06404c9f2103ca936310e',
    'content-type': 'application/json',
    'origin': 'https://api.together.ai',
    'priority': 'u=1, i',
    'referer': 'https://api.together.ai/playground/chat/meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    # 'cookie': 'intercom-id-evnv2y8k=fea4d452-f9be-42e0-93e3-1e47a3836362; intercom-device-id-evnv2y8k=2bb3e469-0159-4b6b-a33e-1aea4b51ccb1; __stripe_mid=e0f7c1ba-56c6-44d4-ba1d-cf4611453eb43cf922; state-csrf=z4pfq6gvoqmg92gkq6bljm; together_auth_cookie=%7B%22expires%22%3A%222026-03-11T14%3A02%3A04.928Z%22%2C%22session%22%3A%22b672ad1b7784bcbb96a5b43058d3d4fbd8327f32dd020f12664307eed353c1b86f1e0d515a4c8b2d990dc5017ed1f13cd7514dee6263bcbd9e03446143245ba0c21968f273967cdb73dd6fedb0a9ff2b65a3ed2ce66b2cd4f94053c747be019d93327fa1f6b24bca9a559ba98ec48f2b51c3be242891d86bb670453120eed64e%22%7D; AMP_MKTG_7112ee0414=JTdCJTIycmVmZXJyZXIlMjIlM0ElMjJodHRwcyUzQSUyRiUyRmFjY291bnRzLmdvb2dsZS5jb20lMkYlMjIlMkMlMjJyZWZlcnJpbmdfZG9tYWluJTIyJTNBJTIyYWNjb3VudHMuZ29vZ2xlLmNvbSUyMiU3RA==; intercom-session-evnv2y8k=UWtNaFEraEJ3ZzcydXlwUC94MHhPcGg3eGZ6RXJkM2c3a2J3R1dwUGR4RWRzQnozWFNLQ0tqbW5za0gvU3RodmNZNXh4NVhRL3I5RWhwNjZKRnd5M21XRm9sZUZhTm05ZUUvaXMxZEYrNjQ9LS1OS0dDcFpuZGRCRE5XaWkxcDVZOEtBPT0=--83289f02195d8a45658bb26d7036c1bf9cfe9887; __stripe_sid=7e7f0bab-efaa-4ec6-ae34-2857cccc4f644bc033; AMP_7112ee0414=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjI5NGU0MzFjOS02OTM0LTQwMGItYTk3Ni0yZjEyNzZmNjg4YzklMjIlMkMlMjJ1c2VySWQlMjIlM0ElMjI2N2I4M2E1Y2Q4MzFiZTcxYjAyYjM4MmElMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzQxNzAxNzE5MDE5JTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTc0MTcwMTc1NTU4MSUyQyUyMmxhc3RFdmVudElkJTIyJTNBODklMkMlMjJwYWdlQ291bnRlciUyMiUzQTQlN0Q=',
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