"""One-off Groq connectivity check. Run: docker compose run --rm api python scripts/test_groq.py"""
from __future__ import annotations

from _bootstrap import ensure_backend_on_path

ensure_backend_on_path()

from groq import Groq

from app.core.config import settings


def main() -> None:
    key = settings.GROQ_API_KEY
    print(f"Key present: {bool(key)}")
    if key:
        print(f"Key starts with: {key[:8]}...")
        print(f"Key length: {len(key)}")
    else:
        print("EMPTY KEY")
        return

    client = Groq(api_key=key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Say OK"}],
        max_tokens=10,
    )
    print("Groq works:", response.choices[0].message.content)


if __name__ == "__main__":
    main()
