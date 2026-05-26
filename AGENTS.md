# Luna Chat — Project Rules

## Context
SaaS chatbot for Chilean notaries.
First client: notary in Valparaíso.
The developer orchestrates, the agents build.

## Stack
- **Backend**: FastAPI + Python 3.14
- **Database**: PostgreSQL + pgvector
- **AI Model**: DeepSeek V4 Flash (`deepseek-v4-flash`)
- **Embeddings**: local sentence-transformers (`all-MiniLM-L6-v2`)
- **Frontend**: to be built

## Decisions made — not up for discussion
- DeepSeek API key is centralized in `.env` as `DEEPSEEK_API_KEY`
- Never exposed to the frontend
- Multi-tenant: each client completely isolated by `client_id`
- Conversation history: maximum 6 messages
- Max tokens per response: 600
- No API key per client in database
- Notary classifier parameterizable by client
- Embeddings generated locally, never via external API
- DeepSeek base_url: https://api.deepseek.com
- Model string: deepseek-v4-flash (never use deprecated alias deepseek-chat)

## Token optimization — mandatory
Every chat request must go through this pipeline in order:
1. Exact match in faq_cache → return without calling model
2. Semantic match in pgvector (threshold 0.85) → return cached response
3. Notary classifier (parametrizable per client) → if not relevant, return derivation message
4. RAG top-3 chunks + DeepSeek V4 Flash → max_tokens=600

## Git workflow
- One branch per sprint: feature/sprint0, feature/sprint1, etc.
- Commit after each completed task, not after each file
- Commit format: "Sprint X: short description"
- Merge to develop only after testing
- Main = production only

## Work rules
1. Never do two tasks at the same time
2. Always report which files were touched when finishing a task
3. If there is a conflict with these rules, ask before acting
4. Do not install unapproved libraries without consulting
5. Each sprint is confirmed before starting the next one
6. Never modify main branch directly
7. Always ask before adding a new dependency to requirements.txt

## Sprints
- **Sprint 0**: Technical foundation ✅
- **Sprint 1**: RAG + notary corpus + PDF upload
- **Sprint 2**: Embeddable widget + admin panel
- **Sprint 3**: Google Calendar + scheduling
- **Sprint 4**: Onboarding + pricing + metrics

## What is NOT being built for now
- Native mobile app
- Model fine-tuning
- Own CRM
- ERP integration
- WhatsApp (comes in a later phase)
- Voice chatbot
- Multi-model selection by client (Phase 3)