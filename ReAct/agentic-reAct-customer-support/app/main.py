from fastapi import FastAPI
from pydantic import BaseModel
from .agent import ReActAgent
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="AgenticAI ReAct - Customer Support")
agent = ReActAgent()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post('/chat')
async def chat(req: ChatRequest):
    reply, trace = await agent.handle_message(req.user_id, req.message)
    return {"reply": reply, "agent_trace": trace}