import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.models.user import User
from app.models.client import Client
from app.models.conversation import Conversation
from app.models.faq_cache import FaqCache
from app.models.embedding import DocumentEmbedding
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_user(db_session):
    user = User(
        email="test@notaria.cl",
        hashed_password=hash_password("testpass123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(sample_user):
    return create_access_token(data={"sub": sample_user.email})


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def sample_client(db_session):
    client = Client(
        name="Notaria Valparaiso",
        email="contacto@notaria.cl",
        business_type="notaria chilena",
        is_active=True,
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client


@pytest.fixture
def sample_faq(db_session, sample_client):
    faq = FaqCache(
        client_id=sample_client.id,
        question="cuanto cuesta una escritura",
        answer="El costo de una escritura es de $50.000 CLP.",
        embedding=[0.0] * 384,
    )
    db_session.add(faq)
    db_session.commit()
    db_session.refresh(faq)
    return faq


@pytest.fixture
def sample_document(db_session, sample_client):
    doc = DocumentEmbedding(
        client_id=sample_client.id,
        content="Las escrituras publicas se realizan en horario de oficina.",
        embedding=[0.1] * 384,
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)
    return doc


@pytest.fixture
def sample_conversation(db_session, sample_client):
    conv = Conversation(
        client_id=sample_client.id,
        session_id="test-session-1",
        role="user",
        message="Hola, necesito información",
    )
    db_session.add(conv)
    db_session.commit()
    db_session.refresh(conv)
    return conv
