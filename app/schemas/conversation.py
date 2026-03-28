from pydantic import BaseModel

class MessageInput(BaseModel):
    message: str
    session_id: str | None = None

class MessageResponse(BaseModel):
    message: str
    session_id: str
