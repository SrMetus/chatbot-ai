from pydantic import ValidationError
import pytest
from app.schemas.client import ClientCreate, ClientResponse, ClientUpdate
from app.schemas.user import UserCreate, UserResponse, Token
from app.schemas.conversation import MessageInput, MessageResponse


class TestClientSchemas:
    def test_client_create_valid(self):
        data = ClientCreate(
            name="Notaría Test",
            email="test@notaria.cl",
            business_type="notaría chilena",
        )
        assert data.name == "Notaría Test"
        assert data.phone is None

    def test_client_create_invalid_email(self):
        with pytest.raises(ValidationError):
            ClientCreate(
                name="Test",
                email="invalid-email",
                business_type="notaría",
            )

    def test_client_create_missing_required(self):
        with pytest.raises(ValidationError):
            ClientCreate(name="Test")

    def test_client_response_from_attributes(self):
        data = ClientResponse(
            id=1,
            name="Test",
            email="test@notaria.cl",
            business_type="notaría",
            is_active=True,
        )
        assert data.id == 1

    def test_client_update_all_optional(self):
        data = ClientUpdate()
        assert data.name is None
        assert data.email is None

    def test_client_update_partial(self):
        data = ClientUpdate(name="Solo Nombre")
        assert data.name == "Solo Nombre"
        assert data.email is None


class TestUserSchemas:
    def test_user_create_valid(self):
        data = UserCreate(email="user@notaria.cl", password="secure123")
        assert data.email == "user@notaria.cl"
        assert data.password == "secure123"

    def test_user_response_from_attributes(self):
        data = UserResponse(id=1, email="user@notaria.cl", is_active=True)
        assert data.id == 1

    def test_token_valid(self):
        data = Token(access_token="abc.def.ghi", token_type="bearer")
        assert data.token_type == "bearer"


class TestConversationSchemas:
    def test_message_input_required(self):
        data = MessageInput(message="Hola")
        assert data.message == "Hola"
        assert data.session_id is None

    def test_message_input_with_session(self):
        data = MessageInput(message="Hola", session_id="session-123")
        assert data.session_id == "session-123"

    def test_message_input_missing_message(self):
        with pytest.raises(ValidationError):
            MessageInput()

    def test_message_response(self):
        data = MessageResponse(message="Respuesta", session_id="sid-1")
        assert data.message == "Respuesta"
