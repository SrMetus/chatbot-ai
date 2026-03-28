from fastapi import FastAPI
from app.database import engine, Base
from app.models import user
from app.routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Chatbot AI",
    description="API REST para chatbot inteligente con IA",
    version="0.1.0"
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/")
def root():
    return {"message": "Chatbot AI API"}