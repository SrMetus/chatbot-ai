---
name: git-workflow
description: Follow the project's Git conventions and commit style
---

# git-workflow

Use this skill when committing, branching, or managing Git workflow.

## Commit message format

Follow conventional commits with lowercase prefix:

```
<type>: <short description>
```

Types used in this project:
- `feat:` — new feature
- `chore:` — maintenance, config, deps
- `fix:` — bug fix

Examples from history:
```
feat: JWT authentication - register and login endpoints
feat: client model, schemas and CRUD endpoints
chore: update requirements.txt
```

No scope prefixes. No body paragraphs. Single line only.

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
