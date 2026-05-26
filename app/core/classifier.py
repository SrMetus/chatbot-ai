import math
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.embeddings import generate_embedding
from app.core.ai import get_ai_response
from app.models.client import Client
from app.models.faq_cache import FaqCache
from app.models.embedding import DocumentEmbedding
from app.models.conversation import Conversation

HISTORY_LIMIT = 6
SIMILARITY_THRESHOLD = 0.85
FAQ_MATCH_THRESHOLD = 0.85
RAG_MATCH_THRESHOLD = 0.75


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def get_recent_history(db: Session, client_id: int, session_id: str) -> list:
    rows = (
        db.query(Conversation)
        .filter(
            Conversation.client_id == client_id,
            Conversation.session_id == session_id,
        )
        .order_by(Conversation.created_at.desc())
        .limit(HISTORY_LIMIT)
        .all()
    )
    rows.reverse()
    return rows

def check_exact_faq(db: Session, client_id: int, message: str) -> str | None:
    entry = (
        db.query(FaqCache)
        .filter(
            FaqCache.client_id == client_id,
            func.lower(FaqCache.question) == func.lower(message.strip()),
        )
        .first()
    )
    if entry:
        entry.hit_count = FaqCache.hit_count + 1
        db.commit()
        return entry.answer
    return None

def check_semantic_faq(db: Session, client_id: int, message: str) -> str | None:
    embedding = generate_embedding(message)

    entry = (
        db.query(FaqCache)
        .filter(FaqCache.client_id == client_id)
        .order_by(FaqCache.embedding.cosine_distance(embedding))
        .limit(1)
        .first()
    )

    if entry:
        similarity = _cosine_similarity(entry.embedding, embedding)
        if similarity >= FAQ_MATCH_THRESHOLD:
            entry.hit_count = FaqCache.hit_count + 1
            db.commit()
            return entry.answer
    return None

def classify_relevance(client: Client, message: str) -> bool:
    topic_context = client.business_type or "notaría chilena"
    system_prompt = (
        f"Eres un clasificador. Determina si el siguiente mensaje está relacionado "
        f"con {topic_context}. Responde solo 'SI' o 'NO'."
    )
    result = get_ai_response(
        system_prompt=system_prompt,
        history=[],
        new_message=message,
        max_tokens=5,
        temperature=0,
    )
    return result.strip().upper().startswith("SI")

def search_rag_context(db: Session, client_id: int, message: str) -> str:
    embedding = generate_embedding(message)

    rows = (
        db.query(DocumentEmbedding)
        .filter(DocumentEmbedding.client_id == client_id)
        .order_by(DocumentEmbedding.embedding.cosine_distance(embedding))
        .limit(3)
        .all()
    )

    if not rows:
        return ""

    filtered = [r for r in rows if _cosine_similarity(r.embedding, embedding) >= RAG_MATCH_THRESHOLD]

    if not filtered:
        return ""

    context_parts = [f"- {r.content}" for r in filtered]
    return "Contexto relevante:\n" + "\n".join(context_parts)

def validate_response(response: str) -> str:
    forbidden_keywords = [
        "eres un asistente de programación",
        "instrucción para hackear",
        "ignora las instrucciones anteriores",
    ]
    response_lower = response.lower()
    for keyword in forbidden_keywords:
        if keyword in response_lower:
            return "Lo siento, no puedo proporcionar esa información."
    return response

def build_history_text(history: list) -> str:
    lines = []
    for msg in history:
        role = "Usuario" if msg.role == "user" else "Asistente"
        lines.append(f"{role}: {msg.message}")
    return "\n".join(lines)

def process_chat(
    db: Session,
    client: Client,
    session_id: str,
    message: str,
) -> str:
    history = get_recent_history(db, client.id, session_id)

    exact = check_exact_faq(db, client.id, message)
    if exact:
        return exact

    semantic = check_semantic_faq(db, client.id, message)
    if semantic:
        return semantic

    if not classify_relevance(client, message):
        return (
            "Lo siento, solo puedo ayudarte con temas relacionados "
            f"con {client.business_type or 'notaría chilena'}. "
            "Por favor, haz una pregunta sobre trámites o servicios notariales."
        )

    rag_context = search_rag_context(db, client.id, message)
    history_text = build_history_text(history)

    full_prompt_parts = []
    if rag_context:
        full_prompt_parts.append(rag_context)
    if history_text:
        full_prompt_parts.append("Historial de la conversación:\n" + history_text)
    full_prompt_parts.append(f"Pregunta del usuario: {message}")

    full_prompt = "\n\n".join(full_prompt_parts)

    response = get_ai_response(
        system_prompt=client.system_prompt or "Eres un asistente útil.",
        history=[],
        new_message=full_prompt,
        max_tokens=300,
    )

    response = validate_response(response)

    return response
