# agentverse_sdk/server.py

from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, Any, List, Union
import threading
import logging
import json
from queue import Queue
from flask import Flask, request, jsonify
from flask_cors import CORS
from fetchai.crypto import Identity
from fetchai.registration import register_with_agentverse
from fetchai.communication import parse_message_from_agent, send_message_to_agent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@dataclass
class AgentMetadata:
    """Metadata for agent registration"""
    title: str
    readme: str  # Developer provides the complete readme XML

@dataclass
class ServerConfig:
    """Configuration for the agent server"""
    host: str = "0.0.0.0"
    port: int = 5001
    cors_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000"])
    debug: bool = False

class AgentServer:
    """
    A server that registers an agent with Agentverse and provides:
    - A webhook to receive messages from other agents
    - Custom endpoints for direct API access
    - Message handling and routing
    """
    
    def __init__(
        self,
        config: ServerConfig,
        metadata: AgentMetadata,
        agent_key: str,
        agentverse_token: str,
    ):
        """
        Initialize the agent server
        
        Args:
            config: Server configuration
            metadata: Agent metadata including title and readme
            agent_key: Secret key for agent identity
            agentverse_token: AgentVerse API token
        """
        self.config = config
        self.metadata = metadata
        self.agent_key = agent_key
        self.agentverse_token = agentverse_token
        
        # Initialize components
        self.app = Flask(__name__)
        self.identity = None
        self.message_queue = Queue()
        self.response_handlers: Dict[str, Callable] = {}
        
        # Setup
        self._setup_cors()
        self._init_routes()
        
    def _setup_cors(self):
        """Configure CORS for API endpoints"""
        CORS(
            self.app,
            resources={
                r"/api/*": {
                    "origins": self.config.cors_origins,
                    "methods": ["GET", "POST", "OPTIONS"],
                    "allow_headers": ["Content-Type", "Authorization"],
                    "max_age": 3600
                }
            }
        )

    def _init_routes(self):
        """Initialize default API routes"""
        
        @self.app.route("/api/webhook", methods=["POST"])
        def webhook():
            try:
                data = request.get_data().decode("utf-8")
                logger.info(f"Received webhook data: {data[:100]}...")
                
                message = parse_message_from_agent(data)
                logger.info(f"Message from {message.sender}: {message.payload}")
                
                # Put message in queue for processing
                self.message_queue.put(message)
                
                # Process specific handlers if registered
                if message.sender in self.response_handlers:
                    try:
                        result = self.response_handlers[message.sender](message.payload)
                        logger.info(f"Handler for {message.sender} executed: {result}")
                    except Exception as e:
                        logger.error(f"Error in message handler: {str(e)}")
                
                return jsonify({"status": "success"})
            except Exception as e:
                logger.error(f"Webhook error: {str(e)}", exc_info=True)
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/health", methods=["GET"])
        def health_check():
            """Health check endpoint"""
            status = "healthy" if self.identity else "initializing"
            return jsonify({
                "status": status,
                "agent_address": self.identity.address if self.identity else None
            })

    def _init_agent(self):
        """Initialize and register the agent with AgentVerse"""
        try:
            if not self.agent_key or not self.agentverse_token:
                raise ValueError("Missing required API keys")
            
            # Create identity
            self.identity = Identity.from_seed(self.agent_key, 0)
            logger.info(f"Created agent identity with address: {self.identity.address}")
            
            # Register with AgentVerse
            webhook_url = f"http://{self.config.host}:{self.config.port}/api/webhook"
            logger.info(f"Registering agent with webhook URL: {webhook_url}")
            
            register_with_agentverse(
                identity=self.identity,
                url=webhook_url,
                agentverse_token=self.agentverse_token,
                agent_title=self.metadata.title,
                readme=self.metadata.readme
            )
            
            logger.info(f"Agent '{self.metadata.title}' registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Agent initialization failed: {str(e)}", exc_info=True)
            raise

    def register_handler(self, agent_address: str, handler: Callable):
        """Register a handler for messages from a specific agent"""
        self.response_handlers[agent_address] = handler
        logger.info(f"Registered handler for agent: {agent_address}")

    def register_endpoint(self, path: str, handler: Callable, methods=None):
        """Register a custom endpoint with the server"""
        if not path.startswith('/'):
            path = f'/api/{path}'
            
        methods = methods or ["POST"]
        logger.info(f"Registering custom endpoint: {path} (methods: {methods})")
        
        def endpoint_wrapper():
            try:
                data = request.get_json() if request.is_json else {}
                logger.info(f"Received request to {path}: {data}")
                
                result = handler(data)
                return jsonify(result)
            except Exception as e:
                logger.error(f"Endpoint error: {str(e)}", exc_info=True)
                return jsonify({"error": str(e)}), 500
        
        self.app.route(path, methods=methods)(endpoint_wrapper)

    def send_message(self, recipient: str, payload: Dict[str, Any]) -> bool:
        """Send message to another agent"""
        if not self.identity:
            logger.error("Cannot send message: Agent not initialized")
            return False
            
        try:
            send_message_to_agent(self.identity, recipient, payload)
            logger.info(f"Message sent to {recipient}: {payload}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}", exc_info=True)
            return False

    def start(self):
        """Start the server in a background thread"""
        # Initialize the agent first
        self._init_agent()
        
        def run_server():
            try:
                logger.info(f"Starting server on {self.config.host}:{self.config.port}")
                self.app.run(
                    host=self.config.host,
                    port=self.config.port,
                    debug=self.config.debug,
                    use_reloader=False
                )
            except Exception as e:
                logger.error(f"Server error: {str(e)}", exc_info=True)
                raise

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        logger.info(f"Server started on {self.config.host}:{self.config.port}")
        return server_thread


# agentverse_sdk/__init__.py

from .server import AgentServer, ServerConfig, AgentMetadata

__version__ = "0.1.0"