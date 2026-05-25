from pydantic import BaseModel, EmailStr

class ClientBase(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    business_type: str
    system_prompt: str | None = None

class ClientCreate(ClientBase):
    pass

class ClientResponse(ClientBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class ClientUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    business_type: str | None = None
    system_prompt: str | None = None
