import os
import logging
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from weaviate import WeaviateClient
from weaviate.connect import ConnectionParams
from utils.intent_check import is_prompt_unclear
from functools import lru_cache
from memory.thread_manager import ThreadMemory
from contextlib import asynccontextmanager
from utils.openai_client import get_llm_response
import logging
from datetime import datetime
from typing import List, Dict

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ella")

# Weaviate Setup
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
GRPC_PORT = 50051

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI application lifespan context manager. Initializes Weaviate client and thread memory.
    """
    try:
        client = WeaviateClient(
            connection_params=ConnectionParams.from_url(WEAVIATE_URL, grpc_port=GRPC_PORT)
        )
        client.connect(skip_init_checks=True)

        chat_schema = {
            "class": "ChatMessage",
            "description": "A single user or assistant message from the chat thread.",
            "vectorizer": "text2vec-transformers",
            "moduleConfig": {
                "text2vec-transformers": {
                    "poolingStrategy": "masked_mean",
                    "vectorizeClassName": False
                }
            },
            "properties": [
                {"name": "author", "dataType": ["text"], "description": "Who said it"},
                {"name": "message", "dataType": ["text"], "description": "Content"},
                {"name": "timestamp", "dataType": ["date"], "description": "When it was sent"}
            ]
        }

        if not client.schema.contains({"class": "ChatMessage"}):
            client.schema.create_class(chat_schema)
            logger.info("✅ Created ChatMessage schema in Weaviate.")
        else:
            logger.info("🔁 ChatMessage schema already exists.")

        app.state.client = client
        app.state.memory = ThreadMemory()
        logger.info("✅ Connected to Weaviate and initialized thread memory.")
        yield
    except Exception as e:
        logger.error(f"❌ Failed to connect to Weaviate: {e}")
        raise
    finally:
        if hasattr(app.state, "client"):
            app.state.client.close()
            logger.info("Closed Weaviate connection")

# FastAPI App
app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility
@lru_cache(maxsize=128)
def cached_is_prompt_unclear(message: str) -> bool:
    """
    Returns True if the prompt is considered unclear by the intent check module.
    """
    return is_prompt_unclear(message)

# Semantic Recall Helper
def fetch_semantic_recall(client: WeaviateClient, query_text: str, top_k: int = 3) -> List[Dict[str, str]]:
    """
    Fetches semantically similar messages using Weaviate's nearText.

    Args:
        client (WeaviateClient): Connected Weaviate client.
        query_text (str): Text to find semantic matches for.
        top_k (int): Number of messages to retrieve.

    Returns:
        List[dict]: List of messages with author, message, and timestamp.
    """
    try:
        collection = client.collections.get("ChatMessage")
        response = collection.query.near_text(
            concepts=[query_text],
            limit=top_k,
            return_properties=["author", "message", "timestamp"]
        )
        return [
            {
                "author": obj.properties["author"],
                "message": obj.properties["message"],
                "timestamp": obj.properties["timestamp"]
            }
            for obj in response.objects
        ]
    except Exception as e:
        logger.error(f"Error during semantic recall: {e}")
        return []

# Routes
@app.post("/chat")
async def chat(request: Request) -> dict:
    """
    Handles user messages, stores them, performs semantic recall, and generates assistant response.
    """
    try:
        body = await request.json()
        message = body.get("message", "")
        author = body.get("author", "")

        if not message.strip():
            raise HTTPException(status_code=400, detail="Message is empty.")

        if cached_is_prompt_unclear(message):
            return {"message": "Could you be a little more specific?"}

        memory = getattr(request.app.state, "memory", None)
        if not memory:
            raise HTTPException(status_code=500, detail="Thread memory not initialized.")

        memory.add(author, message)
        context = memory.get_messages()

        client = request.app.state.client
        client.data_object.create(
            data_object={
                "author": author,
                "message": message,
                "timestamp": datetime.now().astimezone().isoformat()
            },
            class_name="ChatMessage"
        )

        # Semantic recall
        recalled = fetch_semantic_recall(client, message)
        semantic_context = "\n".join([f"{r['author']}: {r['message']}" for r in recalled])
        full_prompt = f"{semantic_context}\n\nUser: {message}"

        response = await get_llm_response(full_prompt)

        memory.add("assistant", response)
        client.data_object.create(
            data_object={
                "author": "assistant",
                "message": response,
                "timestamp": datetime.now().astimezone().isoformat()
            },
            class_name="ChatMessage"
        )
        return {"context": context, "response": response}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /chat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/memory")
async def get_memory(request: Request) -> dict:
    """
    Retrieves all messages from thread memory.
    """
    memory = getattr(request.app.state, "memory", None)
    if not memory:
        raise HTTPException(status_code=500, detail="Thread memory not initialized.")
    return {"messages": memory.get_messages()}

@app.post("/memory/clear")
async def clear_memory(request: Request) -> dict:
    """
    Clears all messages from the thread memory.
    """
    memory = getattr(request.app.state, "memory", None)
    if not memory:
        raise HTTPException(status_code=500, detail="Thread memory not initialized.")
    memory.clear()
    return {"message": "Thread memory cleared."}
