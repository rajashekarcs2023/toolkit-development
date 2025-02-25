import requests
import os
import json


import requests

api_url = "https://agentverse.ai/v1/search/agents"
payload = {
    "search_text": "Tavily search agent",
    "sort": "interactions",
    "direction": "desc",
    "offset": 0,
    "limit": 3
}

# Make the API request to find the most relevant agent
response = requests.post(api_url, json=payload)

if response.status_code == 200:
    data = response.json()
    print(data)
    agents = data.get("agents", [])
    print(agents)
else:
    print(f"Error: {response.status_code}")
    print(response.text)