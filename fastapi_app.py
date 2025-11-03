# main.py
import uvicorn
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
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8080)
