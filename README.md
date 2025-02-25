# ToolKit SDK Documentation

## Introduction

The AgentVerse SDK provides a simplified interface for developing, deploying, and managing agents within the AgentVerse ecosystem. It abstracts away the complexities of server setup, agent registration, and message handling, allowing developers to focus on building agent functionality.

This documentation covers the installation, core concepts, API reference, toolkit SDK.

## Table of Contents

1. Installation
2. Core Concepts
3. Getting Started
4. API Reference
   - ServerConfig
   - AgentMetadata
   - AgentServer
5. Examples


## 1. Installation

### Prerequisites

- Python 3.7+
- fetchai package

### Installation Steps

```bash
# Install the Fetch.ai package
pip install fetchai

# Additional dependencies
pip install flask flask-cors
```

### Environment Setup

Create a `.env` file with the following variables:

```
AGENT_KEY=your_agent_seed_phrase
AGENTVERSE_API_KEY=your_agentverse_api_key
```
## 2. Core Concepts

### Agents in AgentVerse

Agents are autonomous entities that can communicate with other agents through the AgentVerse ecosystem. Each agent:
- Has a unique identity and address
- Can send and receive messages
- Can expose custom API endpoints
- Is registered with AgentVerse for discovery

### Agent Components

The SDK structures agents with the following components:

1. **Configuration** - Defines server settings like host, port, and CORS
2. **Metadata** - Defines agent information like title and capabilities
3. **Handlers** - Functions that process requests and messages
4. **Server** - Manages HTTP endpoints and message routing

### Communication Methods

Agents can communicate in two ways:

1. **AgentVerse Protocol** - Agents exchange messages using the Fetch.ai communication protocol
2. **HTTP API** - Agents expose REST endpoints for direct interaction

### Agent Lifecycle

1. **Initialization** - Configure the agent and set up handlers
2. **Registration** - Register with AgentVerse to be discoverable
3. **Operation** - Process incoming messages and API requests
4. **Termination** - Shut down gracefully when no longer needed

## 3. Getting Started

### Creating Your First Agent

```python
from agentverse_sdk import AgentServer, ServerConfig, AgentMetadata
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure server
config = ServerConfig(port=5001)

# Define agent metadata
metadata = AgentMetadata(
    title="Hello World Agent",
    readme="""
        <description>A simple agent that responds with a greeting.</description>
        <use_cases>
            <use_case>Demonstrate basic agent functionality</use_case>
        </use_cases>
        <payload_requirements>
            <description>Expected message format</description>
            <payload>
                <requirement>
                    <parameter>name</parameter>
                    <description>Your name</description>
                </requirement>
            </payload>
        </payload_requirements>
    """
)

# Initialize the server
server = AgentServer(
    config=config,
    metadata=metadata,
    agent_key=os.getenv("AGENT_KEY"),
    agentverse_token=os.getenv("AGENTVERSE_API_KEY")
)

# Define a handler for greetings
def handle_greeting(data):
    name = data.get("name", "World")
    return {"message": f"Hello, {name}!"}

# Register the endpoint
server.register_endpoint("greet", handle_greeting)

# Start the server
server.start()

# Keep the main thread alive
try:
    import time
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Server shutting down...")
```

### Testing Your Agent

You can test your agent with a simple HTTP request:

```bash
curl -X POST http://localhost:5001/api/greet \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice"}'
```

## 4. API Reference

### ServerConfig

A dataclass that configures the agent's server settings.

```python
@dataclass
class ServerConfig:
    host: str = "0.0.0.0"  # Host to bind the server to
    port: int = 5001       # Port to listen on
    cors_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000"])  # Allowed CORS origins
    debug: bool = False    # Enable debug mode
```

#### Parameters:

- `host` (str): The host address to bind the server to. Default is "0.0.0.0" (all interfaces).
- `port` (int): The port number to listen on. Default is 5001.
- `cors_origins` (List[str]): List of allowed origins for CORS. Default is ["http://localhost:3000"].
- `debug` (bool): Enable Flask debug mode. Default is False.

### AgentMetadata

A dataclass that defines the agent's metadata for registration.

```python
@dataclass
class AgentMetadata:
    title: str          # Agent title
    readme: str         # Agent readme in XML format
```

#### Parameters:

- `title` (str): The title of the agent.
- `readme` (str): XML-formatted readme describing the agent's capabilities and payload requirements.

#### Readme Format:

```xml
<description>Agent description text</description>
<use_cases>
    <use_case>Use case 1</use_case>
    <use_case>Use case 2</use_case>
</use_cases>
<payload_requirements>
    <description>Expected payload format</description>
    <payload>
        <requirement>
            <parameter>parameter_name</parameter>
            <description>Parameter description</description>
        </requirement>
    </payload>
</payload_requirements>
```

### AgentServer

The main class that handles server initialization, endpoint registration, and message routing.

```python
class AgentServer:
    def __init__(self, config, metadata, agent_key, agentverse_token):
        # Initialize server with config and credentials
        
    def register_handler(self, agent_address, handler):
        # Register a handler for messages from a specific agent
        
    def register_endpoint(self, path, handler, methods=None):
        # Register a custom HTTP endpoint
        
    def send_message(self, recipient, payload):
        # Send a message to another agent
        
    def start(self):
        # Start the server in a background thread
```

#### Methods:

**`__init__(config, metadata, agent_key, agentverse_token)`**

Initialize a new agent server.

- **Parameters:**
  - `config` (ServerConfig): Server configuration.
  - `metadata` (AgentMetadata): Agent metadata.
  - `agent_key` (str): Secret key for agent identity.
  - `agentverse_token` (str): AgentVerse API key.

**`register_handler(agent_address, handler)`**

Register a handler function for messages from a specific agent.

- **Parameters:**
  - `agent_address` (str): The address of the sender agent.
  - `handler` (Callable): Function that processes messages from this agent.
  
- **Handler Signature:**
  ```python
  def handler(payload: Dict[str, Any]) -> Any:
      # Process payload
      return result
  ```

**`register_endpoint(path, handler, methods=None)`**

Register a custom HTTP endpoint.

- **Parameters:**
  - `path` (str): Endpoint path (will be prefixed with '/api/' if not starting with '/').
  - `handler` (Callable): Function that processes requests to this endpoint.
  - `methods` (List[str], optional): HTTP methods to support. Default is ["POST"].

- **Handler Signature:**
  ```python
  def handler(data: Dict[str, Any]) -> Dict[str, Any]:
      # Process request data
      return response_data
  ```

**`send_message(recipient, payload)`**

Send a message to another agent.

- **Parameters:**
  - `recipient` (str): Address of the recipient agent.
  - `payload` (Dict[str, Any]): Message payload.
  
- **Returns:**
  - `bool`: True if successful, False otherwise.

**`start()`**

Initialize the agent and start the server in a background thread.

- **Returns:**
  - `threading.Thread`: The server thread.

## 5. Examples

### Creating a Calculator Agent

```python
from agentverse_sdk import AgentServer, ServerConfig, AgentMetadata
import os
from dotenv import load_dotenv

load_dotenv()

# Configure the server
config = ServerConfig(port=5003)

# Define agent metadata
metadata = AgentMetadata(
    title="Calculator Agent",
    readme="""
        <description>An agent that performs basic arithmetic operations</description>
        <use_cases>
            <use_case>Perform addition, subtraction, multiplication, and division</use_case>
        </use_cases>
        <payload_requirements>
            <description>Calculator operation format</description>
            <payload>
                <requirement>
                    <parameter>operation</parameter>
                    <description>Operation to perform (add, subtract, multiply, divide)</description>
                </requirement>
                <requirement>
                    <parameter>a</parameter>
                    <description>First number</description>
                </requirement>
                <requirement>
                    <parameter>b</parameter>
                    <description>Second number</description>
                </requirement>
            </payload>
        </payload_requirements>
    """
)

# Initialize the server
server = AgentServer(
    config=config,
    metadata=metadata,
    agent_key=os.getenv("AGENT_KEY"),
    agentverse_token=os.getenv("AGENTVERSE_API_KEY")
)

# Define calculator handler
def calculate(data):
    operation = data.get("operation")
    a = float(data.get("a", 0))
    b = float(data.get("b", 0))
    
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            return {"error": "Division by zero"}
        result = a / b
    else:
        return {"error": "Unknown operation"}
    
    return {"result": result}

# Register the endpoint
server.register_endpoint("calculate", calculate)

# Start the server
server.start()

# Keep the main thread alive
import time
while True:
    time.sleep(1)
```

### Multi-Agent Communication Example

This example demonstrates how to set up two agents that communicate with each other:

```python
# agent_a.py
from agentverse_sdk import AgentServer, ServerConfig, AgentMetadata
import os
from dotenv import load_dotenv

load_dotenv()

# Configure the server
config = ServerConfig(port=5001)
metadata = AgentMetadata(
    title="Agent A",
    readme="<description>Sends requests to Agent B</description>"
)

# Initialize the server
server = AgentServer(
    config=config,
    metadata=metadata,
    agent_key=os.getenv("AGENT_A_KEY"),
    agentverse_token=os.getenv("AGENTVERSE_API_KEY")
)

# Store Agent B's address
AGENT_B_ADDRESS = os.getenv("AGENT_B_ADDRESS")

# Handler for responses from Agent B
def handle_response_from_b(payload):
    print(f"Received from Agent B: {payload}")
    return {"status": "processed"}

# Register handler for Agent B
if AGENT_B_ADDRESS:
    server.register_handler(AGENT_B_ADDRESS, handle_response_from_b)

# Endpoint to trigger communication
def send_to_b(data):
    message = data.get("message", "Hello from Agent A")
    if AGENT_B_ADDRESS:
        success = server.send_message(AGENT_B_ADDRESS, {"message": message})
        return {"status": "sent" if success else "failed"}
    return {"error": "Agent B address not configured"}

# Register endpoint
server.register_endpoint("send", send_to_b)

# Start the server
server.start()

# Keep the main thread alive
import time
while True:
    time.sleep(1)
```

```python
# agent_b.py
from agentverse_sdk import AgentServer, ServerConfig, AgentMetadata
import os
from dotenv import load_dotenv

load_dotenv()

# Configure the server
config = ServerConfig(port=5002)
metadata = AgentMetadata(
    title="Agent B",
    readme="<description>Responds to messages from Agent A</description>"
)

# Initialize the server
server = AgentServer(
    config=config,
    metadata=metadata,
    agent_key=os.getenv("AGENT_B_KEY"),
    agentverse_token=os.getenv("AGENTVERSE_API_KEY")
)

# Store Agent A's address
AGENT_A_ADDRESS = os.getenv("AGENT_A_ADDRESS")

# Handler for messages from Agent A
def handle_message_from_a(payload):
    message = payload.get("message", "")
    print(f"Received from Agent A: {message}")
    
    # Send response back
    if AGENT_A_ADDRESS:
        server.send_message(AGENT_A_ADDRESS, {
            "response": f"Processed: {message}"
        })
    
    return {"status": "processed"}

# Register handler for Agent A
if AGENT_A_ADDRESS:
    server.register_handler(AGENT_A_ADDRESS, handle_message_from_a)

# Start the server
server.start()

# Keep the main thread alive
import time
while True:
    time.sleep(1)
```

## 6. Troubleshooting

### Common Issues and Solutions

**Agent registration fails**
- Verify that your `AGENT_KEY` and `AGENTVERSE_API_KEY` are correct
- Check network connectivity to the AgentVerse registry
- Ensure your readme XML is properly formatted

**Messages aren't being received**
- Verify that the sender has the correct recipient address
- Check that your webhook URL is publicly accessible
- Ensure your server is running and the port is open

**Custom endpoints aren't working**
- Check the URL path (remember the `/api/` prefix)
- Verify the request payload format
- Check for errors in your handler function

**CORS errors when accessing from frontend**
- Add the frontend origin to `cors_origins` in `ServerConfig`
- Ensure the request includes the correct headers

### Logging

The SDK uses Python's standard logging module. To see more detailed logs:

```python
import logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
```
