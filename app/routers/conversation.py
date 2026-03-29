import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.ai import get_ai_response
from app.schemas.conversation import MessageInput, MessageResponse
from app.models import conversation as conversation_model, client as client_model

router = APIRouter()

@router.post("/{client_id}", response_model=MessageResponse)
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

    ai_response = get_ai_response(
        api_key=db_client.openai_api_key,
        system_prompt=db_client.system_prompt,
        history=history,
        new_message=message.message
    )

    user_message = conversation_model.Conversation(
        client_id=client_id,
        session_id=session_id,
        role="user",
        message=message.message
    )
    db.add(user_message)

    ai_message = conversation_model.Conversation(
        client_id=client_id,
        session_id=session_id,
        role="assistant",
        message=ai_response
    )
    db.add(ai_message)
    
    db.commit()

    return {"message": ai_response, "session_id": session_id}
