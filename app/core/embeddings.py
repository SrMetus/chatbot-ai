import os

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def generate_embedding(text: str) -> list[float]:
    if os.environ.get("DISABLE_EMBEDDINGS", "").lower() == "true":
        return [0.0] * 384
    model = get_embedding_model()
    return model.encode(text).tolist()
