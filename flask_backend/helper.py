import requests

API_KEY = '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'
API_URL = 'https://api.openai.com/v1/chat/completions'

def chat_with_llm(prompt):
    if not prompt:
        return ''

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'gpt-4o-mini',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 2000
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        chat_response = response.json()
        return chat_response['choices'][0]['message']['content']
    return ''

def combine_files_to_string(directory_path):
    combined_content = ""
    file_names = ['insights.md', 'data.md', 'news.md']
    for file_name in file_names:
        file_path = f"{directory_path}/{file_name}"  
        try:
            with open(file_path, 'r') as file:
                content = file.read() 
                combined_content += f"\n\n# Content from {file_name}\n\n"  
                combined_content += content  
        except FileNotFoundError:
            print(f"File {file_name} not found in {directory_path}.")
        except Exception as e:
            print(f"Error reading {file_name}: {e}")

    return combined_content