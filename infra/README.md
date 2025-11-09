# Infra

- Compose file: `infra/docker-compose.yml`
- Env file: `infra/.env`

Run:

```
docker compose -f infra/docker-compose.yml up --build
```

Services:
- backend: FastAPI on `http://localhost:8000`
- frontend: Next.js on `http://localhost:3000`
- db: Postgres 15 (`instantviz`)
- redis: Redis 7

