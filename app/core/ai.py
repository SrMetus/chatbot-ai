def get_ai_response(
    api_key: str,
    system_prompt: str,
    history: list,
    new_message: str
) -> str:
    # Mock temporal para pruebas
    return f"Hola, recibí tu mensaje: '{new_message}'. Soy un mock de IA, pronto seré Claude."