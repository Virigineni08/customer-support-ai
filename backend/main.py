import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))
sys.path.append(os.path.join(os.path.dirname(__file__), "database"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from assistant import answer_query
from db import save_message, get_history
import uuid

app = FastAPI(title="TechMart Customer Support AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

@app.get("/")
def root():
    return {"status": "TechMart Customer Support AI is running"}

@app.post("/chat")
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    result = answer_query(request.message)

    save_message(
        session_id=session_id,
        user_message=request.message,
        ai_response=result["answer"],
        agent_used=result["agent_used"],
        routed_to=result["routed_to"]
    )

    result["session_id"] = session_id
    return result

@app.get("/history/{session_id}")
def history(session_id: str):
    return get_history(session_id)