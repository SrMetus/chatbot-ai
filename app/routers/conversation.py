import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.conversation import MessageInput
from app.models import conversation as conversation_model, client as client_model

router = APIRouter()

@router.post("/{client_id}")
def chat(client_id: int, message: MessageInput, db: Session = Depends(get_db)):
    db_client = db.query(client_model.Client).filter(client_model.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    if db_client.openai_api_key is None:
        raise HTTPException(status_code=400, detail="Client has no API key configured")

    session_id = message.session_id or str(uuid.uuid4())

    history = db.query(conversation_model.Conversation)\
        .filter(
            conversation_model.Conversation.client_id == client_id,
            conversation_model.Conversation.session_id == session_id
        )\
        .order_by(conversation_model.Conversation.created_at)\
    .all()