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
- Max tokens per response: 300
- No API key per client in database
- Notary classifier parameterizable by client

## Work rules
1. Never do two tasks at the same time
2. Always report which files were touched when finishing a task
3. If there is a conflict with these rules, ask before acting
4. Do not install unapproved libraries without consulting
5. Each sprint is confirmed before starting the next one

## Sprints
- **Sprint 0**: Technical foundation (in progress)
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
