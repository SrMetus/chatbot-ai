from pydantic import BaseModel

class MessageInput(BaseModel):
    message: str

class MessageResponse(BaseModel):
    message: str
    session_id: str
