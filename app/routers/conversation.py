import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.classifier import process_chat
from app.schemas.conversation import MessageInput, MessageResponse
from app.models import client as client_model, conversation as conversation_model

router = APIRouter()


@router.post("/{client_id}", response_model=MessageResponse)
def chat(client_id: int, message: MessageInput, db: Session = Depends(get_db)):
    db_client = db.query(client_model.Client).filter(client_model.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    session_id = message.session_id or str(uuid.uuid4())

    ai_response = process_chat(
        db=db,
        client=db_client,
        session_id=session_id,
        message=message.message,
    )

    user_message = conversation_model.Conversation(
        client_id=client_id,
        session_id=session_id,
        role="user",
        message=message.message,
    )
    db.add(user_message)

    ai_message = conversation_model.Conversation(
        client_id=client_id,
        session_id=session_id,
        role="assistant",
        message=ai_response,
    )
    db.add(ai_message)

    db.commit()

    return {"message": ai_response, "session_id": session_id}
