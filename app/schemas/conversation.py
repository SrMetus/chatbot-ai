from pydantic import BaseModel

class MessageBase(BaseModel):
    message: str

class MessageInput(MessageBase):
    pass

class MessageResponse(MessageBase):
    session_id: str
