---
name: git-workflow
description: Follow the project's Git conventions and commit style
---

# git-workflow

Use this skill when committing, branching, or managing Git workflow.

## Commit message format

Follow the project format from AGENTS.md:

```
Sprint X: short description
```

Examples:
```
Sprint 0: JWT authentication - register and login endpoints
Sprint 0: client model, schemas and CRUD endpoints
Sprint 0: update requirements.txt
```

No body paragraphs. Single line only.

## Before committing

1. `git status` — verify only intended files are staged
2. `git diff` — review all changes
3. Do not commit secrets (`.env`, API keys, passwords)
4. Do not force-push
5. Do not commit `venv/` or `__pycache__/` (already in `.gitignore`)

## Branch naming

Feature branches use `feature/<description>` pattern (hyphen-separated):

```
feature/jwt-auth
feature/client-model
feature/ai-integration
```

## Absolute rule

The agent NEVER executes `git commit`, `git push`, or any git operation. The developer does everything manually.

When finishing each task, clearly list the modified/created/deleted files.
