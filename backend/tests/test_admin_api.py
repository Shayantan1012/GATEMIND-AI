import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tests.helpers import auth_header, create_question, make_app, register_and_login_admin


class AdminApiTest(unittest.TestCase):
    def setUp(self):
        self.app, self.client = make_app()

    def test_admin_register_login_dashboard(self):
        login = register_and_login_admin(self.client)
        dashboard = self.client.get("/api/admin/dashboard", headers=auth_header(login["access_token"]))
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.json["data"]["admins"], 1)

    def test_second_admin_requires_bootstrap_token(self):
        register_and_login_admin(self.client)
        blocked = self.client.post(
            "/api/admin/auth/register",
            json={
                "full_name": "Second Admin",
                "email": "second@gatemind.ai",
                "password": "AdminPass123",
                "role": "CONTENT_ADMIN",
            },
        )
        self.assertEqual(blocked.status_code, 403)

        allowed = self.client.post(
            "/api/admin/auth/register",
            headers={"X-Admin-Bootstrap-Token": "bootstrap-secret"},
            json={
                "full_name": "Second Admin",
                "email": "second@gatemind.ai",
                "password": "AdminPass123",
                "role": "CONTENT_ADMIN",
            },
        )
        self.assertEqual(allowed.status_code, 201)

    def test_admin_question_create_and_list(self):
        login = register_and_login_admin(self.client)
        question = create_question(self.client, login["access_token"])
        response = self.client.get("/api/admin/questions", headers=auth_header(login["access_token"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["data"][0]["question_id"], question["question_id"])

    def test_user_token_cannot_access_admin_dashboard(self):
        response = self.client.get("/api/admin/dashboard")
        self.assertEqual(response.status_code, 401)

    def test_content_admin_permissions_are_scoped(self):
        login = register_and_login_admin(self.client, role="CONTENT_ADMIN")
        headers = auth_header(login["access_token"])

        self.assertEqual(self.client.get("/api/admin/rag/documents", headers=headers).status_code, 200)
        self.assertEqual(self.client.get("/api/admin/dashboard", headers=headers).status_code, 403)
        self.assertEqual(self.client.get("/api/admin/users", headers=headers).status_code, 403)
        self.assertEqual(self.client.get("/api/admin/mock-tests", headers=headers).status_code, 403)

    def test_mocktest_admin_permissions_are_scoped(self):
        login = register_and_login_admin(self.client, role="MOCKTEST_ADMIN")
        headers = auth_header(login["access_token"])

        self.assertEqual(self.client.get("/api/admin/mock-tests", headers=headers).status_code, 200)
        self.assertEqual(self.client.get("/api/admin/dashboard", headers=headers).status_code, 403)
        self.assertEqual(self.client.get("/api/admin/users", headers=headers).status_code, 403)
        self.assertEqual(self.client.get("/api/admin/rag/documents", headers=headers).status_code, 403)

    def test_admin_users_rejects_invalid_pagination(self):
        login = register_and_login_admin(self.client)
        response = self.client.get(
            "/api/admin/users?limit=invalid",
            headers=auth_header(login["access_token"]),
        )
        self.assertEqual(response.status_code, 400)

    def test_admin_can_view_users_overview(self):
        login = register_and_login_admin(self.client)
        user_login = self.client.post(
            "/api/auth/register",
            json={
                "full_name": "Student Viewer",
                "email": "viewer@student.com",
                "password": "Student123",
                "mobile_number": "+910000000000",
                "branch": "CSE",
                "target_gate_year": 2028,
            },
        )
        self.assertEqual(user_login.status_code, 201)
        auth_service = self.app.extensions["services"]["auth"]
        otp = next(iter(auth_service.verification_service._otps))
        verified = self.client.post("/api/auth/verify-otp", json={"otp": otp})
        self.assertEqual(verified.status_code, 200)

        overview = self.client.get("/api/admin/users", headers=auth_header(login["access_token"]))
        self.assertEqual(overview.status_code, 200)
        self.assertEqual(overview.json["data"][0]["email"], "viewer@student.com")
        self.assertIn("preferred_subjects", overview.json["data"][0])
        self.assertIn("target_gate_year", overview.json["data"][0])

    def test_admin_can_create_update_publish_list_and_delete_mock_test(self):
        login = register_and_login_admin(self.client)
        token = login["access_token"]
        question = create_question(self.client, token)

        created = self.client.post(
            "/api/admin/mock-tests",
            headers=auth_header(token),
            json={
                "title": "Algorithms Drill",
                "description": "Initial draft",
                "duration_minutes": 45,
                "question_ids": [question["question_id"]],
            },
        )
        self.assertEqual(created.status_code, 201)
        mock_test_id = created.json["data"]["mock_test_id"]

        updated = self.client.put(
            f"/api/admin/mock-tests/{mock_test_id}",
            headers=auth_header(token),
            json={
                "title": "Algorithms Drill Updated",
                "description": "Refined for revision",
                "duration_minutes": 60,
                "question_ids": [question["question_id"]],
            },
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json["data"]["title"], "Algorithms Drill Updated")
        self.assertEqual(updated.json["data"]["duration_minutes"], 60)

        listed = self.client.get("/api/admin/mock-tests", headers=auth_header(token))
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.json["data"][0]["mock_test_id"], mock_test_id)

        published = self.client.post(f"/api/admin/mock-tests/{mock_test_id}/publish", headers=auth_header(token))
        self.assertEqual(published.status_code, 200)
        self.assertTrue(published.json["data"]["is_published"])

        deleted = self.client.delete(f"/api/admin/mock-tests/{mock_test_id}", headers=auth_header(token))
        self.assertEqual(deleted.status_code, 200)

        listed_again = self.client.get("/api/admin/mock-tests", headers=auth_header(token))
        self.assertEqual(listed_again.status_code, 200)
        self.assertEqual(len(listed_again.json["data"]), 0)

    def test_admin_can_manage_inline_mock_test_questions(self):
        login = register_and_login_admin(self.client)
        token = login["access_token"]

        created = self.client.post(
            "/api/admin/mock-tests",
            headers=auth_header(token),
            json={
                "title": "Inline Builder Test",
                "description": "Created directly from mock test form",
                "duration_minutes": 90,
                "questions": [
                    {
                        "question_type": "MCQ",
                        "subject": "Algorithms",
                        "prompt": "What is the time complexity of binary search?",
                        "options": ["O(n)", "O(log n)", "O(n log n)", "O(1)"],
                        "correct_answer": "O(log n)",
                        "marks": 2,
                        "negative_marks": 0.5,
                        "explanation": "Binary search halves the search space.",
                    },
                    {
                        "question_type": "NAT",
                        "subject": "Engineering Mathematics",
                        "prompt": "Enter the value of 6 x 7.",
                        "correct_answer": "42",
                        "marks": 1,
                        "negative_marks": 0,
                    },
                ],
            },
        )
        self.assertEqual(created.status_code, 201)
        self.assertEqual(len(created.json["data"]["questions"]), 2)
        mock_test_id = created.json["data"]["mock_test_id"]
        first_question_id = created.json["data"]["questions"][0]["question_id"]

        updated = self.client.put(
            f"/api/admin/mock-tests/{mock_test_id}",
            headers=auth_header(token),
            json={
                "title": "Inline Builder Test Updated",
                "description": "Updated directly from mock test form",
                "duration_minutes": 75,
                "questions": [
                    {
                        "question_id": first_question_id,
                        "question_type": "MSQ",
                        "subject": "Algorithms",
                        "prompt": "Which of the following are divide and conquer algorithms?",
                        "options": ["Merge Sort", "Quick Sort", "Dijkstra", "Binary Search"],
                        "correct_answer": ["Merge Sort", "Quick Sort", "Binary Search"],
                        "marks": 2,
                        "negative_marks": 0.5,
                    }
                ],
            },
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json["data"]["title"], "Inline Builder Test Updated")
        self.assertEqual(len(updated.json["data"]["questions"]), 1)
        self.assertEqual(updated.json["data"]["questions"][0]["question_type"], "MSQ")

    def test_super_admin_can_clear_logs_and_uploads_without_deleting_profile_images(self):
        login = register_and_login_admin(self.client)
        headers = auth_header(login["access_token"])
        services = self.app.extensions["services"]

        with TemporaryDirectory() as temporary_directory:
            backend_root = Path(temporary_directory)
            upload_root = backend_root / "uploads"
            profile_root = upload_root / "profile-images"
            user_upload_root = upload_root / "users" / "user-1"
            log_root = upload_root / "logs"
            test_output_root = upload_root / "test-output"
            profile_root.mkdir(parents=True)
            user_upload_root.mkdir(parents=True)
            log_root.mkdir(parents=True)
            test_output_root.mkdir(parents=True)
            profile_image = profile_root / "avatar.png"
            uploaded_pdf = user_upload_root / "notes.pdf"
            test_output = test_output_root / "latest-tests.log"
            profile_image.write_bytes(b"profile")
            uploaded_pdf.write_bytes(b"study-document")
            test_output.write_text("test output", encoding="utf-8")
            (log_root / "server.log").write_text("runtime log", encoding="utf-8")
            (log_root / "server.err").write_text("runtime error", encoding="utf-8")

            services["rag_repo"].save_document({"_id": "document-1", "source": "notes.pdf"})
            services["rag_repo"].save_chunks([{"_id": "chunk-1", "document_id": "document-1"}])
            services["rag_repo"].save_conversation(
                {"_id": "conversation-1", "user_id": "user-1", "title": "Study chat"}
            )
            services["rag_repo"].save_chat(
                {"_id": "chat-1", "conversation_id": "conversation-1", "user_id": "user-1"}
            )
            services["storage_maintenance"].upload_folder = upload_root.resolve()

            response = self.client.delete("/api/admin/maintenance/storage", headers=headers)

            self.assertEqual(response.status_code, 200)
            self.assertTrue(profile_image.exists())
            self.assertFalse(uploaded_pdf.exists())
            self.assertFalse(test_output.exists())
            self.assertEqual((log_root / "server.log").read_text(encoding="utf-8"), "")
            self.assertEqual((log_root / "server.err").read_text(encoding="utf-8"), "")
            self.assertEqual(services["rag_repo"].count_documents(), 1)
            self.assertEqual(len(services["rag_repo"].list_chunks()), 1)
            self.assertEqual(services["rag_repo"].conversations.count_documents({}), 1)
            self.assertEqual(services["rag_repo"].chats.count_documents({}), 1)
            self.assertEqual(response.json["data"]["mongodb_records_deleted"], 0)
            self.assertTrue(response.json["data"]["rag_data_preserved"])
            self.assertTrue(response.json["data"]["profile_images_preserved"])

    def test_non_super_admin_cannot_clear_storage(self):
        login = register_and_login_admin(self.client, role="CONTENT_ADMIN")
        response = self.client.delete(
            "/api/admin/maintenance/storage",
            headers=auth_header(login["access_token"]),
        )
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
