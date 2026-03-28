from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import client as client_schema
from app.models import client as client_model

router = APIRouter()

#Endpoint to create a new client, verifying that the email does not already exist.
@router.post("/", response_model=client_schema.ClientResponse)
def create_client(client: client_schema.ClientCreate, db: Session = Depends(get_db)):
    existing = db.query(client_model.Client).filter(client_model.Client.email == client.email).first()  
    if existing:
        raise HTTPException(status_code=400, detail="Client already exists")
    db_client = client_model.Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

#Endpoint to list all existing clients.
@router.get("/", response_model=list[client_schema.ClientResponse])
def read_clients(db: Session = Depends(get_db)):
    return db.query(client_model.Client).all()

#Endpoint to find a client by their id.
@router.get("/{client_id}", response_model=client_schema.ClientResponse)
def read_client(client_id: int, db: Session = Depends(get_db)):
    db_client = db.query(client_model.Client).filter(client_model.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client

#Endpoint to update a client by their id.
@router.patch("/{client_id}", response_model=client_schema.ClientResponse)
def update_client(client_id: int, client: client_schema.ClientUpdate, db: Session = Depends(get_db)):
    db_client = db.query(client_model.Client).filter(client_model.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    for field, value in client.dict(exclude_unset=True).items():
        setattr(db_client, field, value)
    db.commit()
    db.refresh(db_client)
    return db_client

#Endpoint to delete a client by their id. (Not deleted, only its status is changed to inactive)
@router.delete("/{client_id}", response_model=client_schema.ClientResponse)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    db_client = db.query(client_model.Client).filter(client_model.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    db_client.is_active = False
    db.commit()
    return db_client