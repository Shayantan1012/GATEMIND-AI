import unittest

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


if __name__ == "__main__":
    unittest.main()
