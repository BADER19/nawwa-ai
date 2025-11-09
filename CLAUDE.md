# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered instant visualization SaaS platform that converts natural language commands into real-time visual presentations. Users speak or type ideas (e.g., "draw a red circle", "show a parabola and its tangent at x=2") and the system instantly renders visuals on a canvas using AI interpretation.

**Core principle**: Replace static presentation tools with live, intelligent visual workspaces that respond to natural language in real-time.

## Architecture

### High-Level Flow
```
User Input → Backend API (/visualize) → AI Interpretation Layer → JSON Visual Spec → Frontend Canvas (Fabric.js) → Persistent Storage (PostgreSQL)
```

### AI Interpretation Pipeline (backend/services/llm_service.py)

The visualization system uses a **multi-tier interpretation strategy** with configurable fallback behavior:

1. **Image Generation** (optional, if `AI_IMAGE_FIRST=true`): DALL-E generates images for complex visual requests
2. **LLM Interpretation**: OpenAI GPT-4o-mini converts commands to structured JSON visual specs
3. **Rule-Based Patterns** (if `AI_DISABLE_RULES=false`): Deterministic handlers for known patterns:
   - Math plots (parabolas, tangent lines, function graphs)
   - Flowcharts and funnels
   - Icon-based visuals (person stick figures, temple facades)
4. **Naive Fallback**: Simple keyword matching for basic shapes when AI is unavailable

The `interpret_with_source()` function orchestrates these layers and returns `(spec, source, error)` where source tracks which interpreter succeeded (image|llm|rules|fallback|error).

### Backend Structure (FastAPI)

- **main.py**: App initialization, CORS, health checks, startup DB/Redis connection handling
- **services/**:
  - `llm_service.py`: OpenAI integration, prompt templates, spec normalization, multi-tier interpretation
  - `rule_interpreter.py`: Deterministic pattern matchers for math plots, flowcharts, icons
  - `image_service.py`: DALL-E integration for image generation
  - `visualize.py`: `/visualize` endpoint (requires JWT)
  - `auth.py`: `/auth/signup`, `/auth/token` endpoints (JWT-based)
  - `workspace.py`: `/workspace` CRUD endpoints (save/load visual state)
  - `db.py`: SQLAlchemy engine/session management
  - `redis_client.py`: Redis connection for caching
  - `config.py`: Environment-based feature flags (AI_IMAGE_FIRST, AI_DISABLE_RULES, AI_REQUIRE)
- **models/**: SQLAlchemy ORM models (User, Workspace)
- **utils/**: JWT handlers, auth dependencies, Pydantic validators

### Frontend Structure (Next.js + TypeScript)

- **pages/app.tsx**: Main workspace page - chat input + canvas + save/load
- **components/Canvas.tsx**: Fabric.js wrapper that renders visual specs (supports circle, rect, line, triangle, ellipse, polygon, polyline, arrow, text, image types)
- **components/ChatInput.tsx**: Text input for natural language commands
- **lib/api.ts**: Axios wrapper with JWT token injection from localStorage

### Visual Spec Schema

All visual interpretations return JSON in this format:
```json
{
  "elements": [
    {
      "type": "circle|rect|line|triangle|ellipse|polygon|polyline|arrow|text|image",
      "x": 100,
      "y": 100,
      "radius": 50,          // for circle
      "width": 120,          // for rect/triangle/ellipse/line/image
      "height": 80,          // for rect/triangle/ellipse/line/image
      "color": "#1e90ff",
      "label": "Text here",  // for text type
      "points": [{"x": 10, "y": 20}, ...],  // for polygon/polyline
      "src": "https://..."   // for image type
    }
  ]
}
```

The `normalize_spec()` function (backend/services/llm_service.py:79) coerces LLM outputs into this schema by:
- Converting type synonyms (rectangle→rect, square→rect, pyramid→triangle, oval→ellipse, arrow→line)
- Inferring missing dimensions with sensible defaults
- Parsing nested properties (r/radius/size, w/width, h/height)
- Ensuring all coordinates are integers

## Development Commands

### Docker (Recommended for Full Stack)
```bash
# Start all services (backend, frontend, Postgres, Redis)
docker compose -f infra/docker-compose.yml up --build

# Backend runs on http://localhost:18001 (mapped from container port 8000)
# Frontend runs on http://localhost:3000
```

### Local Development (Backend)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Backend requires DATABASE_URL, REDIS_URL, JWT_SECRET, OPENAI_API_KEY in environment
```

### Local Development (Frontend)
```bash
cd frontend
npm install
npm run dev

# Frontend requires NEXT_PUBLIC_API_BASE_URL (default: http://localhost:18001)
```

### Linting & Testing
```bash
# Frontend
cd frontend
npm run lint       # ESLint
npm test           # Currently placeholder

# Backend
cd backend
ruff check .       # Python linting
black .            # Python formatting
mypy .             # Optional type checking
pytest -q          # Run tests (test suite location: backend/tests/)
```

## Configuration & Environment Variables

All services require environment variables in `infra/.env`. Key variables:

- **OPENAI_API_KEY**: Required for AI-powered visualization
- **OPENAI_MODEL**: Defaults to `gpt-4o-mini`
- **DATABASE_URL**: PostgreSQL connection (e.g., `postgresql://user:pass@db:5432/nawwa`)
- **REDIS_URL**: Redis connection (e.g., `redis://redis:6379/0`)
- **JWT_SECRET**: Secret key for JWT signing
- **CORS_ORIGINS**: Comma-separated allowed origins (defaults to `http://localhost:3000`)
- **AI_IMAGE_FIRST**: Set `true` to prioritize DALL-E image generation over LLM specs
- **AI_DISABLE_RULES**: Set `true` to skip rule-based interpreters
- **AI_REQUIRE**: Set `true` to reject requests if AI interpretation fails (no fallback)

## Key Patterns & Conventions

### Backend
- **Authentication**: All `/visualize` and `/workspace/*` routes require JWT tokens via `Depends(get_current_user)`
- **Error Handling**: Visualization failures set `X-Interpreter-Source: error` response header; frontend shows "AI visualization failed" message
- **Database Migrations**: SQLAlchemy models auto-create tables on startup via `Base.metadata.create_all()` (main.py:55)
- **Fallback Strategy**: If OpenAI is unavailable, system uses naive keyword matching unless `AI_REQUIRE=true`
- **Type Normalization**: LLM outputs are sanitized through `normalize_spec()` to handle synonyms and missing fields

### Frontend
- **Token Management**: JWT stored in `localStorage.getItem('token')` and auto-injected in axios interceptor (lib/api.ts)
- **Canvas Re-rendering**: Canvas.tsx useEffect dependency on `elements` array triggers full redraw
- **Dynamic Imports**: Fabric.js is imported dynamically to avoid SSR issues with Next.js
- **Workspace Persistence**: Last workspace ID stored in localStorage for quick reload

## Testing Validation Loop (Stage 1 Complete Criteria)

A user should be able to:
1. Navigate to `/auth` and sign up/login
2. Navigate to `/app` workspace
3. Type "draw a blue circle" and submit
4. See the circle appear on canvas
5. Click "Save" button
6. Reload page and click "Load" button
7. See the same visual restored

## Project Development Status

**Current Stage**: Stage 1 (Complete Foundation)
- ✅ End-to-end vertical slice: auth, visualization, canvas rendering, workspace persistence
- ✅ Multi-tier AI interpretation with configurable fallback behavior
- ✅ Support for basic shapes, math plots, flowcharts, images
- ✅ Docker-based deployment

**Future Stages** (Not Yet Implemented):
- Stage 2: Smart Understanding & Rendering (context awareness, more visual types, workspace intelligence)
- Voice input via OpenAI Whisper API
- Real-time collaboration
- Advanced styling/animations
- Billing and OAuth

## Important Notes

- **Design Philosophy**: Functionality over styling - UI is intentionally minimal (plain inputs/buttons)
- **Security**: Never commit secrets; all sensitive values in `.env` (gitignored)
- **AI Dependency**: System gracefully degrades when OpenAI API is unavailable unless `AI_REQUIRE=true`
- **Canvas Coordinates**: Backend uses Cartesian coordinates for math plots but converts to canvas coordinates (x right, y down) for rendering
- **Type Safety**: Backend uses Pydantic models for request/response validation; frontend uses TypeScript interfaces
