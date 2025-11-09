# Stage 1 Usage (Dev)

1) Copy `.env.example` to `.env` and fill values.

2) Start services via Docker:

   docker compose -f infra/docker-compose.yml up --build

   Backend at http://localhost:8000, Frontend at http://localhost:3000

3) Validate loop:
- Auth: POST /auth/signup then /auth/token (via frontend /auth page).
- Visualize: In /app page, enter "draw a red circle" and submit.
- Save: Click Save; then check backend `/workspace` list.

Local dev (without Docker):
- Backend: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`.
- Frontend: `cd frontend && npm install && npm run dev`.

