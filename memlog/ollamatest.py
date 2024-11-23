import requests
import json

url = "http://localhost:11434/api/embed"
headers = {'Content-Type': 'application/json'}
payload = {
    "model": "mxbai-embed-large",
    "input": ["capital of France"]
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    print(json.dumps(response.json(), indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")
