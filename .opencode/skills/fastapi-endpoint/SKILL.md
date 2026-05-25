---
name: fastapi-endpoint
description: Add a FastAPI endpoint following project conventions
---

# fastapi-endpoint

Use this skill when creating or modifying a FastAPI router endpoint.

## Conventions

- Always create a new `APIRouter` in the router file:

  ```python
  router = APIRouter()
  ```

- All endpoint functions are **sync** (`def`, not `async def`).
- Path prefix is set in `main.py` via `app.include_router(..., prefix="/api/v1/{resource}")`.
- The router file goes in `app/routers/`.

## Dependencies

- DB session: `db: Session = Depends(get_db)` from `app.database`.
- JWT auth (mutate endpoints only): `current_user: User = Depends(get_current_user)` from `app.core.security`.

## Public vs protected

| Access | Pattern |
|--------|---------|
| Public | No `current_user` parameter |
| JWT required | Add `current_user: User = Depends(get_current_user)` |

Existing public endpoints: `GET /api/v1/clients/`, `GET /api/v1/clients/{id}`.
All POST/PATCH/DELETE client endpoints are JWT-protected.

## Error handling

```python
from fastapi import HTTPException
raise HTTPException(status_code=404, detail="Not found")
```

## Response

Return a Pydantic schema or a plain dict. The function signature uses `response_model=...` in the decorator.

## Imports pattern

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import <resource> as <resource>_schema
from app.models import <resource> as <resource>_model
```
