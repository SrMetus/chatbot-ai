from openai import OpenAI

def get_ai_response(
    api_key: str,
    system_prompt: str,
    history: list,
    new_message: str
) -> str:
    client = OpenAI(api_key=api_key)

    messages = [{"role": "system", "content": system_prompt}]

    for msg in history:
        messages.append({"role": msg.role, "content": msg.message})

    messages.append({"role": "user", "content": new_message})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=500
    )

    return response.choices[0].message.content