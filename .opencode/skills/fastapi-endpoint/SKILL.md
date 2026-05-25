---
name: fastapi-endpoint
description: Add a FastAPI endpoint following project conventions
---

# fastapi-endpoint

Use this skill when creating or modifying a FastAPI router endpoint.

## Conventions

- Always create a new `APIRouter` in the router file with `prefix` and `tags` on the router itself:

  ```python
  router = APIRouter(prefix="/api/v1/{resource}", tags=["resource"])
  ```

- All endpoint functions are **sync** (`def`, not `async def`) by default. Use `async def` only when calling async libraries (e.g., `httpx.AsyncClient`) with `await`. In doubt, use `def`.
- Path prefix and tags are set on the `APIRouter()` constructor, not on `app.include_router()`.
- The router file goes in `app/routers/`.

## Dependency injection

Use the `Annotated` style for dependencies with `Depends()`:

```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.models import User

SessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
```

Then in endpoints:

```python
@router.get("/")
def list_items(db: SessionDep):
    return db.query(ItemModel).all()

@router.post("/")
def create_item(db: SessionDep, current_user: CurrentUserDep):
    ...
```

## Dependencies

- DB session: `SessionDep = Annotated[Session, Depends(get_db)]` from `app.database`.
- JWT auth (mutate endpoints only): `CurrentUserDep = Annotated[User, Depends(get_current_user)]` from `app.core.security`.

## Public vs protected

| Access | Pattern |
|--------|---------|
| Public | No `current_user` parameter |
| JWT required | Add `current_user: CurrentUserDep` |

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
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import <resource> as <resource>_schema
from app.models import <resource> as <resource>_model
```
