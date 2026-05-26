from pydantic import BaseModel, EmailStr

class ClientBase(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    business_type: str
    bot_name: str = "Luna"
    primary_color: str = "#1a5276"
    welcome_message: str | None = None
    subtitle: str = "Asistente Virtual"
    system_prompt: str | None = None

class PublicClientResponse(BaseModel):
    id: int
    name: str
    business_type: str
    is_active: bool
    bot_name: str
    subtitle: str
    primary_color: str

    class Config:
        from_attributes = True

class WidgetConfig(BaseModel):
    bot_name: str
    primary_color: str
    welcome_message: str | None = None
    subtitle: str
    is_active: bool

    class Config:
        from_attributes = True

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
    bot_name: str | None = None
    primary_color: str | None = None
    welcome_message: str | None = None
    subtitle: str | None = None
    system_prompt: str | None = None
    is_active: bool | None = None
