from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    business_type = Column(String(100), nullable=False)
    bot_name = Column(String(100), nullable=False, default="Luna")
    primary_color = Column(String(7), nullable=False, default="#1a5276")
    welcome_message = Column(String(500), nullable=True)
    subtitle = Column(String(200), nullable=False, default="Asistente Virtual")
    system_prompt = Column(String(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    conversations = relationship("Conversation", back_populates="client")
    document_embeddings = relationship("DocumentEmbedding", back_populates="client")
    faq_entries = relationship("FaqCache", back_populates="client")
