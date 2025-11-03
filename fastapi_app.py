# main.py
'''import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from movie_agent import run_movie_agent, close_agent

app = FastAPI(title="Movies Finder API", version="1.0.0")

class QueryRequest(BaseModel):
    query: str


@app.post("/chat")
async def chat(request: QueryRequest):
    """Send a message to the Movie Recommender agent."""
    try:
        response = await run_movie_agent(request.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
async def shutdown_event():
    await close_agent()


@app.get("/")
async def root():
    return {"message": "Movies Finder API is running"}


if __name__ == "__main__":
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8080)'''

import os
import json
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
from langsmith import traceable

app = FastAPI(title="Movies Finder API", version="1.0.0")

# Initialize global variables
agent = None
client = None
llm = None

@app.on_event("startup")
async def startup_event():
    """Initialize environment and setup MCP + LLM when server starts."""
    global agent, client, llm

    # Load .env for local dev
    if os.path.exists(".env"):
        load_dotenv()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    # LangSmith / LangChain config
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_PROJECT"] = "movies-finder"
    os.environ["LANGUAGE"] = "en-US"

    # Prepare runtime MCP config
    with open("browser_mcp.json", "r") as f:
        config = json.load(f)

    env_vars = config["mcpServers"]["TVRecommender"]["env"]
    env_vars["TMDB_API_KEY"] = TMDB_API_KEY
    env_vars["OPENAI_API_KEY"] = OPENAI_API_KEY
    env_vars["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY

    runtime_config_file = "browser_mcp_runtime.json"
    with open(runtime_config_file, "w") as f:
        json.dump(config, f, indent=2)

    # Initialize MCP client
    client = MCPClient.from_config_file(runtime_config_file)

    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENAI_API_KEY,
        max_tokens=200,
        temperature=0.7,
    )

    # Initialize Agent
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=75,
        memory_enabled=True
    )

    agent.set_system_message(
        "You are an assistant. Always respond strictly in English. "
        "If you receive or retrieve any content in another language, "
        "translate it to English before replying."
    )

    print("✅ FastAPI startup complete: Agent initialized.")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up MCP sessions gracefully."""
    global client
    if client and client.sessions:
        await client.close_all_sessions()
        print("🧹 MCP sessions closed.")


# ----------- Request Models -----------

class QueryRequest(BaseModel):
    query: str


# ----------- Routes -----------

@app.get("/")
async def root():
    return {"message": "Movies Finder API is running!"}


@traceable(project_name="movies-finder")
async def run_agent(user_input: str) -> str:
    """Wrapper to run agent query."""
    global agent
    if not agent:
        raise RuntimeError("Agent not initialized")
    return await agent.run(user_input)


@app.post("/chat")
async def chat_endpoint(req: QueryRequest):
    """Main endpoint for querying the assistant."""
    try:
        response = await run_agent(req.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
async def reset_endpoint():
    """Clear agent memory and reset sessions."""
    global agent, client
    if client and client.sessions:
        await client.close_all_sessions()
    # Reset agent memory (if supported)
    agent.memory_enabled = True
    return {"message": "Session reset successfully."}
