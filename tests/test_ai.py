from unittest.mock import patch, MagicMock
from app.core.ai import _get_client, get_ai_response


class TestAIClient:
    def test_get_client_returns_openai_client(self):
        client = _get_client()
        assert client is not None
        assert client.api_key is not None
        assert client.base_url is not None

    def test_get_client_is_singleton(self):
        c1 = _get_client()
        c2 = _get_client()
        assert c1 is c2


class TestGetAIResponse:
    @patch("app.core.ai._get_client")
    def test_returns_response_from_api(self, mock_get_client):
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Respuesta del asistente."
        mock_client.chat.completions.create.return_value.choices = [mock_choice]
        mock_get_client.return_value = mock_client

        result = get_ai_response(
            system_prompt="Eres un asistente.",
            history=[],
            new_message="Hola",
        )
        assert result == "Respuesta del asistente."

    @patch("app.core.ai._get_client")
    def test_sends_correct_parameters(self, mock_get_client):
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "ok"
        mock_client.chat.completions.create.return_value.choices = [mock_choice]
        mock_get_client.return_value = mock_client

        get_ai_response(
            system_prompt="Sistema",
            history=[],
            new_message="Mensaje",
            max_tokens=300,
            temperature=0.7,
        )

        mock_client.chat.completions.create.assert_called_once()
        kwargs = mock_client.chat.completions.create.call_args[1]
        assert kwargs["max_tokens"] == 300
        assert kwargs["temperature"] == 0.7
        assert kwargs["model"] is not None

    @patch("app.core.ai._get_client")
    def test_builds_messages_with_history(self, mock_get_client):
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "respuesta"
        mock_client.chat.completions.create.return_value.choices = [mock_choice]
        mock_get_client.return_value = mock_client

        from app.models.conversation import Conversation
        from datetime import datetime, timezone

        history = [
            Conversation(
                role="user",
                message="pregunta anterior",
                created_at=datetime.now(timezone.utc),
            ),
            Conversation(
                role="assistant",
                message="respuesta anterior",
                created_at=datetime.now(timezone.utc),
            ),
        ]

        get_ai_response(
            system_prompt="Sistema",
            history=history,
            new_message="nueva pregunta",
        )

        kwargs = mock_client.chat.completions.create.call_args[1]
        messages = kwargs["messages"]
        assert messages[0] == {"role": "system", "content": "Sistema"}
        assert messages[1] == {"role": "user", "content": "pregunta anterior"}
        assert messages[2] == {"role": "assistant", "content": "respuesta anterior"}
        assert messages[3] == {"role": "user", "content": "nueva pregunta"}

    @patch("app.core.ai._get_client")
    def test_handles_empty_response(self, mock_get_client):
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = None
        mock_client.chat.completions.create.return_value.choices = [mock_choice]
        mock_get_client.return_value = mock_client

        result = get_ai_response(
            system_prompt="Sistema",
            history=[],
            new_message="test",
        )
        assert result == ""
