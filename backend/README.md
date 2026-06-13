# GATEMIND AI Backend

Modular Flask backend for authentication, administration, mock tests, performance analytics, and LangChain RAG.

## Architecture

```text
app/
  controllers/       Flask blueprints and HTTP concerns
  models/            Domain entities and factories
  repositories/      MongoDB repository adapters
  services/
    admin/            Admin auth, audit logging, dashboard
    auth/             User authentication service
    notifications/    Email and SMS notification adapters
    security/         Email validation, password hashing, JWT
    users/            User profile service
    verification/     OTP and email verification strategies
    mocktest/         One-file services and evaluation_strategies/
    rag/
      parsers/        One parser class per file
      chunking/       One chunking strategy per file
      embeddings/     Embedding implementations and factory
      vectorstores/   Vector-store interface and adapters
      retrievers/     Retriever interface, implementations, rerankers
      indexing/       Indexing template and concrete pipeline
  schemas/            API serializers
  utils/              Authentication middleware and API responses
```

Every domain/service/repository class has its own file. Import-only facade modules remain for backward compatibility.

The implementation follows the supplied diagram:

- Factory: question creation, document parsers, embedding provider selection
- Strategy: question evaluation, document chunking
- Adapter: Mongo repositories and Mongo vector-store adapter
- Template Method: RAG indexing pipeline
- Builder: RAG context construction
- Observer-style update: mock-test performance updates the user learning profile

## Setup

```powershell
cd backend
.\..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

For development without a running MongoDB server:

```env
MONGO_USE_MOCK=true
```

For persistent storage, keep `MONGO_USE_MOCK=false` and run MongoDB at `MONGO_URI`.

When `OPENAI_API_KEY` is empty, RAG uses local deterministic embeddings and returns retrieved context.
When it is configured, LangChain uses OpenAI embeddings and the configured chat model.

## Main API

### Users

- `POST /api/auth/register`
- `POST /api/auth/verify-otp`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `POST /api/auth/forgot-password`
- `POST /api/auth/reset-password`
- `POST /api/auth/refresh-token`
- `GET|PUT /api/users/profile`
- `GET /api/users/progress`

### Admin

- `POST /api/admin/auth/register`
- `POST /api/admin/auth/login`
- `POST /api/admin/auth/logout`
- `POST /api/admin/auth/refresh-token`
- `GET /api/admin/dashboard`
- `GET /api/admin/users`
- `POST|GET /api/admin/questions`
- `POST /api/admin/mock-tests`
- `POST /api/admin/mock-tests/<id>/publish`
- `POST|GET /api/admin/rag/documents`

The first admin can register directly. Later registrations require `X-Admin-Bootstrap-Token` matching `ADMIN_BOOTSTRAP_TOKEN`.

### Mock Tests

- `GET /api/mock-tests`
- `GET /api/mock-tests/<id>`
- `POST /api/mock-tests/<id>/submit`
- `GET /api/mock-tests/history`

### RAG

- `POST /api/rag/documents`
- `GET /api/rag/documents`
- `POST /api/rag/chat`
- `GET /api/rag/history`

Students can upload up to five files directly from the chat composer and scope questions to selected attachments.
Supported uploads: PDF, TXT, Markdown, CSV, JSON, PNG, JPG, JPEG, and WebP. Image OCR is enabled when Pillow and Tesseract are installed.

## Tests

```powershell
python run_tests.py
```

Runtime logs are stored in `uploads/logs/server.log` and `uploads/logs/server.err`.
Test output from `run_tests.py` is stored in `uploads/test-output/latest-tests.log`.
These files remain until a super admin uses the storage cleanup action.

The integration test covers admin creation, question bank, mock-test publishing, user OTP verification, submission/evaluation, performance personalization, document indexing, RAG retrieval, citations, and dashboard analytics.

## AWS Backend Deployment

The backend includes a production Gunicorn container, backend-only GitHub Actions CI/CD, and Terraform for ECS Fargate.

See [`../infrastructure/backend/README.md`](../infrastructure/backend/README.md) for the complete deployment procedure.
