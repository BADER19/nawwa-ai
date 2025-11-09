# Instant Visualization SaaS (Stage 1)

End-to-end vertical slice: sign up/login, send a command (e.g., "draw a red circle"), render on canvas, and save workspace.

Quick start
- Copy `infra/.env` and set values.
- Run: `docker compose -f infra/docker-compose.yml up --build`
- Open `http://localhost:3000` → use `/auth` then `/app`.

Services
- backend: FastAPI (`/auth`, `/visualize`, `/workspace`)
- frontend: Next.js (Fabric.js canvas)
- db: Postgres; redis: Redis

Notes
- `/visualize` and `/workspace/*` require JWT.
- OpenAI GPT-4o powers interpretation; falls back to a naive parser if unavailable.

