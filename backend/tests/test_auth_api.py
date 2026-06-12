import unittest

from tests.helpers import auth_header, make_app, register_and_login_student


class AuthApiTest(unittest.TestCase):
    def setUp(self):
        self.app, self.client = make_app()

    def test_register_rejects_missing_fields(self):
        response = self.client.post("/api/auth/register", json={"email": "bad@test.com"})
        self.assertEqual(response.status_code, 400)

    def test_register_verify_login_profile_and_logout(self):
        login = register_and_login_student(self.app, self.client)
        token = login["access_token"]
        profile = self.client.get("/api/users/profile", headers=auth_header(token))
        self.assertEqual(profile.status_code, 200)

        logout = self.client.post("/api/auth/logout", json={"refresh_token": login["refresh_token"]})
        self.assertEqual(logout.status_code, 200)

    def test_refresh_token_creates_access_token(self):
        login = register_and_login_student(self.app, self.client)
        response = self.client.post("/api/auth/refresh-token", json={"refresh_token": login["refresh_token"]})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json["data"])

    def test_refresh_token_cannot_access_profile_directly(self):
        login = register_and_login_student(self.app, self.client)
        response = self.client.get("/api/users/profile", headers=auth_header(login["refresh_token"]))
        self.assertEqual(response.status_code, 401)

    def test_change_password_flow(self):
        login = register_and_login_student(self.app, self.client)
        token = login["access_token"]
        changed = self.client.post(
            "/api/users/change-password",
            headers=auth_header(token),
            json={"old_password": "Student123", "new_password": "Better123"},
        )
        self.assertEqual(changed.status_code, 200)

        relogin = self.client.post("/api/auth/login", json={"email": "student@example.com", "password": "Better123"})
        self.assertEqual(relogin.status_code, 200)


if __name__ == "__main__":
    unittest.main()
