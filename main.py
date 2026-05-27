import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base, get_db
from app.models import client as client_model, conversation as conversation_model
from app.models.user import User
from app.core.security import hash_password
from app.routers import auth, admin as admin_router, client as client_router, conversation as conversation_router, document as document_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Chatbot AI",
    description="API REST para chatbot inteligente con IA",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router.router)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(client_router.router)
app.include_router(conversation_router.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(document_router.router, prefix="/api/v1/documents", tags=["documents"])

app.mount("/admin", StaticFiles(directory="frontend/admin", html=True), name="admin")
app.mount("/widget", StaticFiles(directory="frontend/widget", html=True), name="widget")

@app.on_event("startup")
def seed_admin():
    db = next(get_db())
    try:
        user = db.query(User).filter(User.email == "admin@test.cl").first()
        if not user:
            db.add(User(email="admin@test.cl", hashed_password=hash_password("pass123")))
            db.commit()
            print("Admin user created: admin@test.cl")
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Chatbot AI API"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)