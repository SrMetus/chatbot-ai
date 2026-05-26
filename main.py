from fastapi import FastAPI
from app.database import engine, Base
from app.models import client as client_model, conversation as conversation_model
from app.routers import auth, client as client_router, conversation as conversation_router, document as document_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Chatbot AI",
    description="API REST para chatbot inteligente con IA",
    version="0.1.0"
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(client_router.router, prefix="/api/v1/clients", tags=["clients"])
app.include_router(conversation_router.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(document_router.router, prefix="/api/v1/documents", tags=["documents"])

@app.get("/")
def root():
    return {"message": "Chatbot AI API"}