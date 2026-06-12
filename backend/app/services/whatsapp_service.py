import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

async def send_whatsapp_message(to_phone: str, text: str):
    """
    Sends a message via Meta Cloud API (WhatsApp).
    Requires WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID in settings.
    """
    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        logger.warning("WhatsApp credentials missing. Skipping message.")
        return False

    url = f"https://graph.facebook.com/v19.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": text},
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {e}")
        return False
