# GATEMIND AI Backend

Flask backend structured around the authentication and user-management classes from the provided diagram.

## Setup

```powershell
cd backend
.\..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

If PowerShell rejects the activation script, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\..\.venv\Scripts\Activate.ps1
```

## Endpoints

- `GET /api/health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `POST /api/auth/forgot-password`
- `POST /api/auth/verify-otp`
- `POST /api/auth/verify-email`
- `POST /api/auth/refresh-token`
- `GET /api/users/profile`
- `PUT /api/users/profile`
- `POST /api/users/change-password`
- `GET /api/users/progress`
- `GET /api/users/mock-test-history`

## Notes

This version uses an in-memory repository so it runs immediately. Replace `InMemoryUserRepository` with a database-backed implementation when you are ready for persistence.
