import requests
import json
import time

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

def chat_interface():
    messages = [
        {'content': 'hello', 'role': 'user'},
        {'content': '<think>\n\n</think>\n\nHello! How can I assist you today? 😊', 'role': 'assistant'},
    ]

    while True:
        user_input = input("\033[94mYou:\033[0m ")
        messages.append({'content': user_input, 'role': 'user'})

        json_data = {
            'model': 'meta-llama/Llama-Vision-Free',
            'max_tokens': None,
            'temperature': 0.7,
            'top_p': 0.7,
            'top_k': 50,
            'repetition_penalty': 1,
            'stream_tokens': True,
            'stop': ['<｜end▁of▁sentence｜>'],
            'messages': messages,
            'stream': True,
        }

        with requests.post('https://api.together.ai/inference', cookies=cookies, headers=headers, json=json_data, stream=True) as response:
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
                                        print(f"\033[92m{choice['text']}\033[0m", end="", flush=True)  # Print text tokens continuously in green
                            except json.JSONDecodeError:
                                continue
                messages.append({'content': assistant_response, 'role': 'assistant'})
                print()  # Print a newline after the assistant's response
            elif response.status_code == 429:
                time.sleep(0.5)
            else:
                print(f"Unexpected status code: {response.status_code}")
                break

chat_interface()