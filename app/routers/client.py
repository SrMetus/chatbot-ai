from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import client as client_schema
from app.models import client as client_model
from app.core.security import get_current_user
from app.models.user import User

SessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]

router = APIRouter(prefix="/api/v1/clients", tags=["clients"])

@router.post("/", response_model=client_schema.ClientResponse)
def create_client(client: client_schema.ClientCreate, db: SessionDep, current_user: CurrentUserDep):
    """Create a new client after verifying the email is not already taken.

    Args:
        client: Client creation payload.

    Returns:
        ClientResponse: The newly created client.

    Raises:
        HTTPException 400: If a client with the same email already exists.
    """
    existing = db.query(client_model.Client).filter(client_model.Client.email == client.email).first()  
    if existing:
        raise HTTPException(status_code=400, detail="Client already exists")
    db_client = client_model.Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.get("/", response_model=list[client_schema.PublicClientResponse])
def read_clients(db: SessionDep):
    """List all clients (public-safe view).

    Returns:
        list[PublicClientResponse]: All clients in the database.
    """
    return db.query(client_model.Client).all()

@router.get("/{client_id}", response_model=client_schema.PublicClientResponse)
def read_client(client_id: int, db: SessionDep):
    """Retrieve a single client by ID.

    Args:
        client_id: Target client ID.

    Returns:
        PublicClientResponse: The matching client.

    Raises:
        HTTPException 404: If the client does not exist.
    """
    db_client = db.query(client_model.Client).filter(client_model.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client

@router.get("/{client_id}/widget-config", response_model=client_schema.WidgetConfig)
def widget_config(client_id: int, db: SessionDep):
    """Return the public widget configuration for a client.

    Used by the embeddable chat widget to fetch branding and behaviour
    settings without exposing sensitive fields.

    Args:
        client_id: Target client ID.

    Returns:
        WidgetConfig: The client's widget settings.

    Raises:
        HTTPException 404: If the client does not exist.
    """
    db_client = db.query(client_model.Client).filter(client_model.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client

@router.patch("/{client_id}", response_model=client_schema.ClientResponse)
def update_client(client_id: int, client: client_schema.ClientUpdate, db: SessionDep, current_user: CurrentUserDep):
    """Partially update a client.

    Only the fields provided in the payload are applied.

    Args:
        client_id: Target client ID.
        client: Patch payload with fields to update.

    Returns:
        ClientResponse: The updated client.

    Raises:
        HTTPException 404: If the client does not exist.
    """
    db_client = db.query(client_model.Client).filter(client_model.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    for field, value in client.model_dump(exclude_unset=True).items():
        setattr(db_client, field, value)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.delete("/{client_id}", response_model=client_schema.ClientResponse)
def delete_client(client_id: int, db: SessionDep, current_user: CurrentUserDep):
    """Soft-delete a client by marking it as inactive.

    Args:
        client_id: Target client ID.

    Returns:
        ClientResponse: The client with is_active set to False.

    Raises:
        HTTPException 404: If the client does not exist.
    """
    db_client = db.query(client_model.Client).filter(client_model.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    db_client.is_active = False
    db.commit()
    return db_client
