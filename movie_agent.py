# movie_agent.py
import os
import json
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langsmith import traceable
from mcp_use import MCPAgent, MCPClient

# Initialize globals (only once)
_client = None
_llm = None
_agent = None

async def setup_agent():
    global _client, _llm, _agent

    if _agent:  # already initialized
        return _agent

    if os.path.exists(".env"):
        load_dotenv()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    # Inject env vars into MCP config
    with open("browser_mcp.json", "r") as f:
        config = json.load(f)
    env_vars = config["mcpServers"]["TVRecommender"]["env"]
    env_vars["TMDB_API_KEY"] = TMDB_API_KEY
    env_vars["OPENAI_API_KEY"] = OPENAI_API_KEY
    env_vars["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY

    runtime_config_file = "browser_mcp_runtime.json"
    with open(runtime_config_file, "w") as f:
        json.dump(config, f, indent=2)

    # Initialize MCP client and LLM
    _client = MCPClient.from_config_file(runtime_config_file)
    _llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENAI_API_KEY,
        max_tokens=200,
        temperature=0.7,
    )
    _agent = MCPAgent(
        llm=_llm,
        client=_client,
        max_steps=75,
        memory_enabled=True
    )
    _agent.set_system_message(
        "You are an assistant. Always respond strictly in English. "
        "If you receive or retrieve any content in another language, "
        "translate it to English before replying."
    )

    return _agent


@traceable(project_name="movies-finder")
async def run_movie_agent(query: str):
    agent = await setup_agent()
    result = await agent.run(query)
    return result


async def close_agent():
    """Close MCP sessions gracefully."""
    global _client
    if _client and hasattr(_client, "sessions"):
        await _client.close_all_sessions()
