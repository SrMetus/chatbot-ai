from unittest.mock import patch, MagicMock
import app.core.embeddings
from app.core.embeddings import get_embedding_model, generate_embedding


class TestEmbeddingModel:
    def setup_method(self):
        app.core.embeddings._model = None

    def test_get_model_returns_model(self):
        with patch("app.core.embeddings.SentenceTransformer") as mock_st:
            mock_instance = MagicMock()
            mock_st.return_value = mock_instance
            model = get_embedding_model()
            assert model is mock_instance
            mock_st.assert_called_once_with("all-MiniLM-L6-v2")

    def test_get_model_is_singleton(self):
        with patch("app.core.embeddings.SentenceTransformer") as mock_st:
            mock_instance = MagicMock()
            mock_st.return_value = mock_instance
            m1 = get_embedding_model()
            m2 = get_embedding_model()
            assert m1 is m2
            mock_st.assert_called_once()


class TestGenerateEmbedding:
    def test_returns_list_of_floats(self):
        with patch("app.core.embeddings.get_embedding_model") as mock_get:
            mock_model = MagicMock()
            mock_model.encode.return_value.tolist.return_value = [0.1] * 384
            mock_get.return_value = mock_model

            result = generate_embedding("Hola mundo")
            assert isinstance(result, list)
            assert len(result) == 384
            assert all(isinstance(v, float) for v in result)

    def test_calls_encode_with_text(self):
        with patch("app.core.embeddings.get_embedding_model") as mock_get:
            mock_model = MagicMock()
            mock_get.return_value = mock_model

            generate_embedding("Texto de prueba")
            mock_model.encode.assert_called_once_with("Texto de prueba")
