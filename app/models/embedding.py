from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from pgvector.sqlalchemy import Vector

class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    client = relationship("Client", back_populates="document_embeddings")
