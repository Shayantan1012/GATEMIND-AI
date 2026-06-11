import io
import unittest

import mongomock

from app import create_app
from app.config import Config


class TestConfig(Config):
    TESTING = True
    MONGO_USE_MOCK = True
    OPENAI_API_KEY = ""
    SECRET_KEY = "test-secret"


class BackendFlowTest(unittest.TestCase):
    def setUp(self):
        database = mongomock.MongoClient()["gatemind_test"]
        self.app = create_app(TestConfig, database=database)
        self.client = self.app.test_client()

    def test_complete_backend_flow(self):
        admin = self.client.post(
            "/api/admin/auth/register",
            json={
                "full_name": "Main Admin",
                "email": "admin@gatemind.ai",
                "password": "AdminPass123",
                "role": "SUPER_ADMIN",
            },
        )
        self.assertEqual(admin.status_code, 201)

        admin_login = self.client.post(
            "/api/admin/auth/login",
            json={"email": "admin@gatemind.ai", "password": "AdminPass123"},
        )
        admin_token = admin_login.json["data"]["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        question = self.client.post(
            "/api/admin/questions",
            headers=admin_headers,
            json={
                "question_type": "MCQ",
                "prompt": "What is 2 + 2?",
                "subject": "Engineering Mathematics",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "4",
                "marks": 2,
                "negative_marks": 0.5,
            },
        )
        self.assertEqual(question.status_code, 201)
        question_id = question.json["data"]["question_id"]

        mock_test = self.client.post(
            "/api/admin/mock-tests",
            headers=admin_headers,
            json={"title": "Math Basics", "question_ids": [question_id], "duration_minutes": 10},
        )
        self.assertEqual(mock_test.status_code, 201)
        mock_test_id = mock_test.json["data"]["mock_test_id"]
        published = self.client.post(
            f"/api/admin/mock-tests/{mock_test_id}/publish",
            headers=admin_headers,
        )
        self.assertEqual(published.status_code, 200)

        registered = self.client.post(
            "/api/auth/register",
            json={
                "full_name": "Student User",
                "email": "student@example.com",
                "password": "Student123",
                "mobile_number": "+910000000000",
                "branch": "CSE",
                "target_gate_year": 2027,
            },
        )
        self.assertEqual(registered.status_code, 201)
        auth_service = self.app.extensions["services"]["auth"]
        otp = next(iter(auth_service.verification_service._otps))
        verified = self.client.post("/api/auth/verify-otp", json={"otp": otp})
        self.assertEqual(verified.status_code, 200)

        login = self.client.post(
            "/api/auth/login",
            json={"email": "student@example.com", "password": "Student123"},
        )
        user_token = login.json["data"]["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        submission = self.client.post(
            f"/api/mock-tests/{mock_test_id}/submit",
            headers=user_headers,
            json={"answers": [{"question_id": question_id, "answer": "4"}]},
        )
        self.assertEqual(submission.status_code, 200)
        self.assertEqual(submission.json["data"]["percentage"], 100.0)
        history = self.client.get("/api/mock-tests/history", headers=user_headers)
        self.assertEqual(history.status_code, 200)
        self.assertEqual(len(history.json["data"]), 1)

        indexed = self.client.post(
            "/api/admin/rag/documents",
            headers=admin_headers,
            data={
                "subject": "Engineering Mathematics",
                "file": (
                    io.BytesIO(b"The sum of two and two is four. Addition combines quantities."),
                    "math-notes.txt",
                ),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(indexed.status_code, 201)

        rag_answer = self.client.post(
            "/api/rag/chat",
            headers=user_headers,
            json={"query": "What is the sum of two and two?"},
        )
        self.assertEqual(rag_answer.status_code, 200)
        self.assertTrue(rag_answer.json["data"]["citations"])

        dashboard = self.client.get("/api/admin/dashboard", headers=admin_headers)
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.json["data"]["mock_test_attempts"], 1)


if __name__ == "__main__":
    unittest.main()
