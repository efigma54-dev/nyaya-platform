from fastapi import APIRouter, Request, Query, HTTPException
from app.services.chat_service import answer_query
from app.services.whatsapp_service import send_whatsapp_message
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Verify token for Meta webhook setup
VERIFY_TOKEN = "nyaya_secret_token"

@router.get("/webhook")
async def verify_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    raise HTTPException(403, "Verification failed")

@router.post("/webhook")
async def handle_whatsapp_message(request: Request):
    """
    Handles incoming WhatsApp messages.
    """
    data = await request.json()
    try:
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        message = value.get("messages", [{}])[0]
        
        if message:
            sender_id = message.get("from")
            text = message.get("text", {}).get("body")
            
            if text:
                # Get answer from AI
                result = await answer_query(text)
                answer = result["answer"]
                
                # Send back to WhatsApp
                await send_whatsapp_message(sender_id, answer)
                
    except Exception as e:
        logger.error(f"Error handling WhatsApp webhook: {e}")
        
    return {"status": "ok"}
