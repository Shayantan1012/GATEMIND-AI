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
- `POST /api/auth/reset-password`
- `POST /api/auth/verify-otp`
- `POST /api/auth/refresh-token`
- `GET /api/users/profile`
- `PUT /api/users/profile`
- `POST /api/users/change-password`
- `GET /api/users/progress`
- `GET /api/users/mock-test-history`

## Notes

This version uses a MongoDB-backed repository for persistence. Set `MONGO_URI` and `MONGO_DB_NAME` in the environment to configure the MongoDB connection.

SMS OTP delivery is supported via Twilio environment variables:

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_FROM_NUMBER`

Example Twilio settings:

```env
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_FROM_NUMBER=+1234567890
```

If Twilio variables are not set, SMS output will be printed to the console for development and testing.
