from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from pgvector.sqlalchemy import Vector

class FaqCache(Base):
    __tablename__ = "faq_cache"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    question = Column(String(500), nullable=False)
    answer = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)
    hit_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    client = relationship("Client", back_populates="faq_entries")
