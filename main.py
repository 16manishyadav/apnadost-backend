# main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict
from firebase_utils import verify_firebase_token
import firebase_admin
from firebase_admin import firestore, auth
import httpx
import logging
import traceback

# Add import for Firestore server timestamp sentinel
try:
    from google.cloud.firestore_v1 import SERVER_TIMESTAMP
except ImportError:
    SERVER_TIMESTAMP = None

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with Vercel URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request body model
class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = Field(default_factory=list)  # Optional: previous chat history

# Initialize Firestore client
firestore_client = firestore.client()

# Set Gemini API key (for production, use environment variable)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = os.getenv("GEMINI_API_URL")

@app.get("/")
def root():
    return {"message": "ApnaDost API live"}

@app.post("/api/chat")
async def chat_endpoint(request: Request, chat: ChatRequest):
    # 1. Verify Firebase ID token and get UID
    uid = verify_firebase_token(request)
    # uid = "test-user"  # For testing without token verification

    # 2. Prepare messages for Gemini
    # Add system prompt for prompt engineering
    system_prompt = (
        "You are a friendly, empathetic mental health companion. "
        "Respond like a caring human, not an AI. "
        "Keep your answers short, friendly, and conversational. "
        "Use appropriate emojis to express warmth, encouragement, and empathy, but don't overdo it. "
        "Avoid giving lists or step-by-step instructions unless the user specifically asks for them. "
        "Do not mention you are an AI or language model. "
        "If the user expresses distress, respond with empathy and encouragement. "
        "Prefer short, natural sentences."
    )
    prompt = f"system: {system_prompt}\n"
    if chat.history:
        for msg in chat.history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt += f"{role}: {content}\n"
    prompt += f"user: {chat.message}\nassistant:"

    # 3. Call Gemini API via REST
    try:
        if not GEMINI_API_URL:
            raise HTTPException(status_code=500, detail="GEMINI_API_URL is not set. Please check your environment variables or .env file.")
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": GEMINI_API_KEY
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(GEMINI_API_URL, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            # Extract the model's reply
            ai_message = result["candidates"][0]["content"]["parts"][0]["text"] if "candidates" in result and result["candidates"] and "content" in result["candidates"][0] and "parts" in result["candidates"][0]["content"] and result["candidates"][0]["content"]["parts"] else ""
    except httpx.HTTPStatusError as e:
        logging.error("Gemini API HTTP error: %s", e.response.text)
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Gemini API error: {e.response.text}")
    except Exception as e:
        logging.error("Gemini API general error: %s", str(e))
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

    # 4. Store chat in Firestore
    chat_ref = firestore_client.collection("users").document(uid).collection("chats")
    chat_ref.add({
        "message": chat.message,
        "response": ai_message,
        "timestamp": SERVER_TIMESTAMP
    })

    # 5. Return AI response
    return {"response": ai_message}
