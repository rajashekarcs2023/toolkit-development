import os
import requests
import argparse
import json
from dotenv import load_dotenv
from fetchai.crypto import Identity
from fetchai.communication import send_message_to_agent

# Load environment variables
load_dotenv()

# Get the client credentials
CLIENT_KEY = os.getenv("CLIENT_KEY")
AGENT_ADDRESS = None  # We'll get this from command-line args

def send_direct_api_request(query: str):
    """Test the agent using its HTTP API endpoint"""
    try:
        response = requests.post(
            "http://localhost:5002/api/search",
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "error", 
                "error": f"HTTP {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def send_agentverse_message(query: str):
    """Test the agent using Agentverse messaging protocol"""
    if not CLIENT_KEY:
        return {"status": "error", "error": "Missing CLIENT_KEY environment variable"}
    
    if not AGENT_ADDRESS:
        return {"status": "error", "error": "Missing agent address"}
    
    try:
        # Create identity
        client_identity = Identity.from_seed(CLIENT_KEY, 0)
        
        # Send message
        payload = {"query": query}
        send_message_to_agent(
            client_identity,
            AGENT_ADDRESS,
            payload
        )
        
        return {"status": "success", "message": "Message sent to agent. Check your webhook for response."}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Test the Tavily Search Agent")
    parser.add_argument("query", help="The search query to send to the agent")
    parser.add_argument("--method", choices=["api", "agentverse"], default="api",
                        help="The method to use for testing (api or agentverse)")
    parser.add_argument("--agent-address", help="The agent's address (required for agentverse method)")
    
    args = parser.parse_args()
    
    # Set the agent address if provided
    global AGENT_ADDRESS
    AGENT_ADDRESS = args.agent_address
    
    # Check if agent address is provided when using agentverse method
    if args.method == "agentverse" and not AGENT_ADDRESS:
        print("Error: --agent-address is required when using the agentverse method")
        return
    
    # Execute the test
    if args.method == "api":
        result = send_direct_api_request(args.query)
    else:
        result = send_agentverse_message(args.query)
    
    # Print the result
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()