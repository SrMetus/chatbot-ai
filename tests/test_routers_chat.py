from unittest.mock import patch


class TestChat:
    @patch("app.routers.conversation.process_chat")
    def test_chat_public_endpoint(self, mock_process, client, sample_client):
        mock_process.return_value = "Respuesta del asistente."
        response = client.post(
            f"/api/v1/chat/{sample_client.id}",
            json={"message": "Hola, necesito ayuda"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Respuesta del asistente."
        assert "session_id" in data

    @patch("app.routers.conversation.process_chat")
    def test_chat_returns_session_id(self, mock_process, client, sample_client):
        mock_process.return_value = "Respuesta."
        response = client.post(
            f"/api/v1/chat/{sample_client.id}",
            json={"message": "Hola", "session_id": "mi-session"},
        )
        assert response.status_code == 200
        assert response.json()["session_id"] == "mi-session"

    @patch("app.routers.conversation.process_chat")
    def test_chat_generates_session_id_if_not_provided(self, mock_process, client, sample_client):
        mock_process.return_value = "Respuesta."
        response = client.post(
            f"/api/v1/chat/{sample_client.id}",
            json={"message": "Hola"},
        )
        assert response.status_code == 200
        assert len(response.json()["session_id"]) > 0

    def test_chat_client_not_found(self, client):
        response = client.post(
            "/api/v1/chat/99999",
            json={"message": "Hola"},
        )
        assert response.status_code == 404

    @patch("app.routers.conversation.process_chat")
    def test_chat_saves_both_messages(self, mock_process, client, sample_client, db_session):
        mock_process.return_value = "Respuesta AI."
        client.post(
            f"/api/v1/chat/{sample_client.id}",
            json={"message": "Mensaje de prueba"},
        )
        from app.models.conversation import Conversation
        messages = db_session.query(Conversation).filter(
            Conversation.client_id == sample_client.id
        ).all()
        assert len(messages) >= 2
        roles = [m.role for m in messages[-2:]]
        assert "user" in roles and "assistant" in roles
