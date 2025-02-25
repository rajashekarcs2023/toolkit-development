import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain_community.chat_models import ChatOpenAI
from langchain.tools.tavily_search import TavilySearchResults
from langchain.utilities.tavily_search import TavilySearchAPIWrapper

# Import our agent server components
from agentverse_sdk.server import AgentServer, ServerConfig, AgentMetadata

# Load environment variables
load_dotenv()

# Required API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AGENT_KEY = os.getenv("AGENT_KEY")
AGENTVERSE_TOKEN = os.getenv("AGENTVERSE_API_KEY1")

class TavilySearchAgent:
    """LangChain agent that performs Tavily searches"""
    
    def __init__(self):
        # Initialize LangChain components
        self.llm = ChatOpenAI(temperature=0.7, openai_api_key=OPENAI_API_KEY)
        search = TavilySearchAPIWrapper(tavily_api_key=TAVILY_API_KEY)
        self.search_tool = TavilySearchResults(api_wrapper=search)
        
        # Initialize the agent
        self.agent_chain = initialize_agent(
            [self.search_tool],
            self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
    
    def search(self, query: str) -> Dict[str, Any]:
        """Execute a search query"""
        try:
            result = self.agent_chain.run({"input": query})
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}

def main():
    """Initialize and start the Tavily Search Agent server"""
    
    # Check for required API keys
    if not all([OPENAI_API_KEY, TAVILY_API_KEY, AGENT_KEY, AGENTVERSE_TOKEN]):
        missing = []
        if not OPENAI_API_KEY: missing.append("OPENAI_API_KEY")
        if not TAVILY_API_KEY: missing.append("TAVILY_API_KEY")
        if not AGENT_KEY: missing.append("AGENT_KEY")
        if not AGENTVERSE_TOKEN: missing.append("AGENTVERSE_TOKEN")
        print(f"Missing required API keys: {', '.join(missing)}")
        return
    
    # Create search agent
    search_agent = TavilySearchAgent()
    
    # Define agent metadata
    metadata = AgentMetadata(
        title="Tavily Search Agent",
        readme="""
        ![tag:innovationlab](https://img.shields.io/badge/innovation--lab-3D8BD3)
            <description>An agent that performs web searches using the Tavily API and returns comprehensive results.</description>
            <use_cases>
                <use_case>Find up-to-date information about any topic</use_case>
                <use_case>Research facts and get summarized information</use_case>
                <use_case>Answer questions that require current web data</use_case>
            </use_cases>
            <payload_requirements>
                <description>Send your search query</description>
                <payload>
                    <requirement>
                        <parameter>query</parameter>
                        <description>The search query you want to run</description>
                    </requirement>
                </payload>
            </payload_requirements>
        """
    )
    
    # Create server configuration
    config = ServerConfig(port=5002)
    
    # Initialize the agent server
    server = AgentServer(
        config=config,
        metadata=metadata,
        agent_key=AGENT_KEY,
        agentverse_token=AGENTVERSE_TOKEN
    )
    
    # Define search endpoint handler
    def handle_search(data: dict) -> dict:
        query = data.get("query")
        if not query:
            return {"error": "Missing search query"}
        return search_agent.search(query)
    
    # Register the search endpoint
    server.register_endpoint("search", handle_search)
    
    # Start the server
    server.start()
    
    print(f"Tavily Search Agent running at http://localhost:{config.port}")
    print("Press Ctrl+C to exit")
    
    # Keep the main thread alive
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server shutting down...")

if __name__ == "__main__":
    main()