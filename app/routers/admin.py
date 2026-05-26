from typing import Annotated
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models import client as client_model, conversation as conversation_model, embedding as embedding_model

SessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/stats")
def admin_stats(
    db: SessionDep,
    current_user: CurrentUserDep,
):
    """Return aggregate platform statistics for the admin dashboard.

    Returns:
        dict: Contains total_clients, active_clients, and
            conversations_today (UTC-day count).
    """
    total_clients = db.query(client_model.Client).count()
    active_clients = db.query(client_model.Client).filter(client_model.Client.is_active.is_(True)).count()

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    conversations_today = (
        db.query(conversation_model.Conversation)
        .filter(conversation_model.Conversation.created_at >= today_start)
        .count()
    )

    return {
        "total_clients": total_clients,
        "active_clients": active_clients,
        "conversations_today": conversations_today,
    }


@router.get("/clients/{client_id}/conversations")
def admin_client_conversations(
    client_id: int,
    db: SessionDep,
    current_user: CurrentUserDep,
):
    """Return the last 100 conversation messages for a given client.

    Args:
        client_id: Target client ID.

    Returns:
        list[dict]: Each entry has id, session_id, role, message,
            and created_at (ISO-8601).
    """
    rows = (
        db.query(conversation_model.Conversation)
        .filter(conversation_model.Conversation.client_id == client_id)
        .order_by(conversation_model.Conversation.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": r.id,
            "session_id": r.session_id,
            "role": r.role,
            "message": r.message,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.get("/clients/{client_id}/documents")
def admin_client_documents(
    client_id: int,
    db: SessionDep,
    current_user: CurrentUserDep,
):
    """Return an aggregated list of uploaded documents for a client.

    Groups chunks by source_file and includes chunk count and upload
    timestamp.

    Args:
        client_id: Target client ID.

    Returns:
        list[dict]: Each entry has source_file, chunks_count, and
            created_at (ISO-8601).
    """
    rows = (
        db.query(
            embedding_model.DocumentEmbedding.source_file,
            func.count(embedding_model.DocumentEmbedding.id).label("chunks_count"),
            func.max(embedding_model.DocumentEmbedding.created_at).label("created_at"),
        )
        .filter(embedding_model.DocumentEmbedding.client_id == client_id)
        .group_by(embedding_model.DocumentEmbedding.source_file)
        .order_by(func.max(embedding_model.DocumentEmbedding.created_at).desc())
        .all()
    )
    return [
        {
            "source_file": r.source_file,
            "chunks_count": r.chunks_count,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
