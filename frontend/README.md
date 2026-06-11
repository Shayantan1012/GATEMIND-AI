# GATEMIND AI Frontend

Vite + React frontend integrated with the Flask backend.

## Setup

```powershell
cd frontend
npm install
npm run dev
```

The dev server runs at:

```text
http://127.0.0.1:5173
```

During development, Vite proxies `/api` requests to:

```text
http://127.0.0.1:5001
```

Override the proxy target with:

```powershell
$env:VITE_BACKEND_URL="http://127.0.0.1:5000"
npm run dev
```

## Included Screens

- Student register, OTP verify, login, password reset
- Student profile and progress
- Published mock-test list, attempt, submit, and results
- Personalized RAG chat with citations
- Admin login and bootstrap registration
- Admin dashboard, question bank, mock-test creation/publish
- RAG document upload and indexed document list

Redux Toolkit is used for auth/session state and backend-loaded dashboard/profile/mock-test/RAG data.
