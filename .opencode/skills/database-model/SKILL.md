---
name: database-model
description: Create or modify SQLAlchemy models with pgvector support
---

# database-model

Use this skill when creating or modifying a SQLAlchemy model.

## Base

All models inherit from `app.database.Base` (SQLAlchemy `DeclarativeBase`).

## Table naming

```python
__tablename__ = "snake_case_plural"  # e.g. "users", "document_embeddings"
```

Exception: `faq_cache` uses singular.

## Column conventions

| Type | Import | Example |
|------|--------|---------|
| Standard | `from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime` | `Column(Integer, primary_key=True, index=True)` |
| ForeignKey | `from sqlalchemy import ForeignKey` | `Column(Integer, ForeignKey("clients.id"), nullable=False)` |
| pgvector | `from pgvector.sqlalchemy import Vector` | `Column(Vector(384), nullable=False)` |

## Datetime default

Always use a lambda for `created_at`:

```python
from datetime import datetime, timezone
created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

## Relationships

Add reverse relationship on the child model. Add forward relationship on the parent (`Client`).

```python
from sqlalchemy.orm import relationship

# On child:
client = relationship("Client", back_populates="document_embeddings")

# On parent (Client model):
document_embeddings = relationship("DocumentEmbedding", back_populates="client")
```

## Registration

Add the model to `app/models/__init__.py`:

```python
from app.models.<module> import <ModelClass>
```
