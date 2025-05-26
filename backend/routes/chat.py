# backend/routes/chat.py

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from utils.intent_check import is_prompt_unclear

router = APIRouter()

@router.post("/chat")
async def chat(request: Request) -> JSONResponse:
    try:
        body = await request.json()
        user_input = body.get("message", "")

        if is_prompt_unclear(user_input):
            return JSONResponse({
                "message": "Just to clarify — could you be more specific about what you're referring to?"
            })

        # Placeholder: this is where you'd connect the real LLM response
        return JSONResponse({"message": f"✨ Echo: {user_input}"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
