---
name: rag-pipeline
description: Work with the RAG + classifier chat pipeline
---

# rag-pipeline

Use this skill when modifying the chat processing pipeline or adding new retrieval logic.

## Pipeline location

All pipeline logic lives in `app/core/classifier.py`. The entry point is `process_chat()`.

## Processing order

1. `get_recent_history(db, client_id, session_id)` — last 6 messages, reversed
2. `check_exact_faq(db, client_id, message)` — case-insensitive ILIQL match on `faq_cache.question`
3. `check_semantic_faq(db, client_id, message)` — cosine distance via pgvector `<=>`, threshold **0.85**
4. `classify_relevance(client, message)` — calls DeepSeek with `max_tokens=5, temperature=0`; parametrizable via `client.business_type`
5. `search_rag_context(db, client_id, message)` — pgvector cosine on `document_embeddings`, top-3, threshold **0.75**
6. `get_ai_response(...)` — DeepSeek V4 Flash, `max_tokens=300`
7. `validate_response(response)` — output guardrail with forbidden keywords

> **Critical rule:** If the pipeline resolves in steps 2 or 3 (exact FAQ or semantic), DO NOT call DeepSeek under any circumstances. Only go to step 6 if the previous steps did not resolve.

## Thresholds

| Step | Threshold | Location |
|------|-----------|----------|
| FAQ semantic match | 0.85 | `faq_cache` → `FAQ_MATCH_THRESHOLD` |
| RAG context match | 0.75 | `document_embeddings` → `RAG_MATCH_THRESHOLD` |

## Embeddings

`generate_embedding(text)` in `app/core/embeddings.py` uses `sentence-transformers` model `all-MiniLM-L6-v2` producing 384-dim vectors.

## AI call

`get_ai_response()` in `app/core/ai.py` uses the OpenAI SDK with `base_url=settings.DEEPSEEK_BASE_URL` and `model=settings.DEEPSEEK_MODEL`, both configurable via `.env`.
