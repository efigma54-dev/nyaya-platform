from groq import Groq
from app.core.config import settings

try:
    client = Groq(api_key=settings.GROQ_API_KEY)
    r = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[{'role': 'user', 'content': 'Say OK'}],
        max_tokens=5
    )
    print('✅ Groq API working:', r.choices[0].message.content)
except Exception as e:
    print('❌ Groq API error:', str(e)[:200])
