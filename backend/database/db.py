import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

client = MongoClient(os.getenv("MONGO_URI"))
db = client["techmart_support"]
conversations = db["conversations"]

def save_message(session_id, user_message, ai_response, agent_used, routed_to):
    conversations.insert_one({
        "session_id": session_id,
        "user_message": user_message,
        "ai_response": ai_response,
        "agent_used": agent_used,
        "routed_to": routed_to,
        "timestamp": datetime.utcnow()
    })

def get_history(session_id):
    results = conversations.find({"session_id": session_id}).sort("timestamp", 1)
    return [
        {
            "user_message": r["user_message"],
            "ai_response": r["ai_response"],
            "agent_used": r["agent_used"],
            "timestamp": r["timestamp"].isoformat()
        }
        for r in results
    ]