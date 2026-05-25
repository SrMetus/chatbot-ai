from openai import OpenAI
from app.core.config import settings

_client = None

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com",
        )
    return _client


def get_ai_response(
    system_prompt: str,
    history: list,
    new_message: str,
    max_tokens: int = 300,
    temperature: float = 0.7,
) -> str:
    client = _get_client()

    messages = [{"role": "system", "content": system_prompt}]

    for msg in history:
        role = "assistant" if msg.role == "assistant" else "user"
        messages.append({"role": role, "content": msg.message})

    messages.append({"role": "user", "content": new_message})

    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    return response.choices[0].message.content or ""
