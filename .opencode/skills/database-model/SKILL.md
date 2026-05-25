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
| Standard | `from sqlalchemy import Column, BigInteger, Boolean, Text, DateTime` | `Column(BigInteger, primary_key=True, index=True)` |
| ForeignKey | `from sqlalchemy import ForeignKey` | `Column(BigInteger, ForeignKey("clients.id"), nullable=False, index=True)` |
| pgvector | `from pgvector.sqlalchemy import Vector` | `Column(Vector(384), nullable=False)` |

**Primary keys**: Prefer `BigInteger` over `Integer` for tables that may grow. Use `Integer` only for small lookup tables.

**Foreign keys**: Always add `index=True` on FK columns. PostgreSQL does not auto-index FKs — missing indexes cause slow cascade deletes and locks.

**Data types**:
- Use `Text` instead of `String` (unless a length limit is semantically required).
- Use `DateTime(timezone=True)` with `TIMESTAMPTZ` on PostgreSQL rather than `DateTime` without timezone.
- Use `BigInteger` for IDs and counts, not `Integer`.

**Indexes**: Beyond the implicit PK and FK indexes, consider:
- **Composite indexes**: `Index("ix_table_col1_col2", "col1", "col2")` — column order matters; put equality-filtered columns first.
- **Partial indexes**: `Index("ix_active_users", "email", postgresql_where=text("is_active = true"))` for queries on a subset of rows.
- **Covering indexes**: `Index("ix_users_email", "email", postgresql_include=["name"])` for index-only scans.

## Datetime default

Always use a lambda for `created_at`:

```python
from datetime import datetime, timezone
created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
```

## Row-Level Security

For multi-tenant isolation at the database level, enable RLS:

```python
# After table creation via event listener
from sqlalchemy import event
from sqlalchemy.schema import DDL

event.listen(
    ModelClass.__table__,
    "after_create",
    DDL("ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY")
)
```

RLS is optional — the application-layer `client_id` filter is the primary isolation mechanism.

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
