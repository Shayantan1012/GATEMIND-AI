import io

import mongomock

from app import create_app
from app.config import Config


class TestConfig(Config):
    TESTING = True
    MONGO_USE_MOCK = True
    OPENAI_API_KEY = ""
    GROQ_API_KEY = ""
    HUGGINGFACE_API_KEY = ""
    SECRET_KEY = "test-secret"
    ADMIN_BOOTSTRAP_TOKEN = "bootstrap-secret"
    ENABLE_FILE_LOGGING = False


def make_app():
    database = mongomock.MongoClient()["gatemind_test"]
    app = create_app(TestConfig, database=database)
    return app, app.test_client()


def register_and_login_student(app, client, email="student@example.com"):
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Student User",
            "email": email,
            "password": "Student123",
            "mobile_number": "+910000000000",
            "branch": "CSE",
            "target_gate_year": 2027,
        },
    )
    assert response.status_code == 201, response.json
    otp = next(iter(app.extensions["services"]["auth"].verification_service._otps))
    verified = client.post("/api/auth/verify-otp", json={"otp": otp})
    assert verified.status_code == 200, verified.json
    login = client.post("/api/auth/login", json={"email": email, "password": "Student123"})
    assert login.status_code == 200, login.json
    return login.json["data"]


def register_and_login_admin(client, email="admin@gatemind.ai", role="SUPER_ADMIN"):
    initial_email = email if role == "SUPER_ADMIN" else "initial-super-admin@gatemind.ai"
    response = client.post(
        "/api/admin/auth/register",
        json={
            "full_name": "Main Admin",
            "email": initial_email,
            "password": "AdminPass123",
            "phone_number": "+919876543210",
            "department": "Platform Operations",
            "job_title": "Platform Administrator",
            "role": "SUPER_ADMIN",
        },
    )
    assert response.status_code == 201, response.json
    initial_login = client.post(
        "/api/admin/auth/login",
        json={"email": initial_email, "password": "AdminPass123"},
    )
    assert initial_login.status_code == 200, initial_login.json

    if role != "SUPER_ADMIN":
        staff = client.post(
            "/api/admin/staff",
            headers=auth_header(initial_login.json["data"]["access_token"]),
            json={
                "full_name": "Scoped Admin",
                "email": email,
                "password": "AdminPass123",
                "phone_number": "+919876543211",
                "department": "Academic Operations",
                "job_title": role.replace("_", " ").title(),
                "role": role,
            },
        )
        assert staff.status_code == 201, staff.json

    login = client.post("/api/admin/auth/login", json={"email": email, "password": "AdminPass123"})
    assert login.status_code == 200, login.json
    return login.json["data"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def create_question(client, admin_token, correct_answer="4"):
    response = client.post(
        "/api/admin/questions",
        headers=auth_header(admin_token),
        json={
            "question_type": "MCQ",
            "prompt": "What is 2 + 2?",
            "subject": "Engineering Mathematics",
            "options": ["3", "4", "5", "6"],
            "correct_answer": correct_answer,
            "marks": 2,
            "negative_marks": 0.5,
        },
    )
    assert response.status_code == 201, response.json
    return response.json["data"]


def create_and_publish_mock_test(client, admin_token, question_id):
    created = client.post(
        "/api/admin/mock-tests",
        headers=auth_header(admin_token),
        json={"title": "Math Basics", "question_ids": [question_id], "duration_minutes": 10},
    )
    assert created.status_code == 201, created.json
    mock_test_id = created.json["data"]["mock_test_id"]
    published = client.post(f"/api/admin/mock-tests/{mock_test_id}/publish", headers=auth_header(admin_token))
    assert published.status_code == 200, published.json
    return mock_test_id


def upload_text_document(client, admin_token):
    return client.post(
        "/api/admin/rag/documents",
        headers=auth_header(admin_token),
        data={
            "subject": "Engineering Mathematics",
            "description": "Clustering notes",
            "file": (io.BytesIO(b"BIRCH is a clustering algorithm. It builds a CF tree."), "notes.txt"),
        },
        content_type="multipart/form-data",
    )
