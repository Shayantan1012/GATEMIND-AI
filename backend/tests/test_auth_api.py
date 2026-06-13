import unittest
import io

from tests.helpers import auth_header, make_app, register_and_login_student


class AuthApiTest(unittest.TestCase):
    def setUp(self):
        self.app, self.client = make_app()

    def test_register_rejects_missing_fields(self):
        response = self.client.post("/api/auth/register", json={"email": "bad@test.com"})
        self.assertEqual(response.status_code, 400)

    def test_register_returns_preview_otp_when_enabled(self):
        response = self.client.post(
            "/api/auth/register",
            json={
                "full_name": "Preview Student",
                "email": "preview@test.com",
                "password": "Student123",
                "mobile_number": "+910000000001",
                "branch": "CSE",
                "target_gate_year": 2027,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertRegex(response.json["data"]["preview_otp"], r"^\d{6}$")
        self.assertEqual(response.json["data"]["user"]["email"], "preview@test.com")

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

    def test_profile_update_supports_branch_subjects_and_image(self):
        login = register_and_login_student(self.app, self.client)
        token = login["access_token"]
        response = self.client.put(
            "/api/users/profile",
            headers=auth_header(token),
            json={
                "branch": "ECE",
                "profile_image": "https://example.com/avatar.png",
                "preferred_subjects": ["Algorithms", "Operating Systems", "Computer Networks"],
                "headline": "Focused GATE aspirant",
                "bio": "Preparing consistently for GATE 2027.",
                "college_name": "Tech Institute",
                "current_semester": 6,
                "graduation_year": 2027,
                "daily_study_goal_hours": 4.5,
                "weekly_mock_test_goal": 3,
                "exam_goal_score": 650,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json["data"]
        self.assertEqual(data["branch"], "ECE")
        self.assertEqual(data["profile_image"], "https://example.com/avatar.png")
        self.assertEqual(data["preferred_subjects"], ["Algorithms", "Operating Systems", "Computer Networks"])
        self.assertEqual(data["current_semester"], 6)
        self.assertEqual(data["daily_study_goal_hours"], 4.5)

    def test_user_can_upload_profile_image_from_device(self):
        login = register_and_login_student(self.app, self.client)
        token = login["access_token"]
        uploaded = self.client.post(
            "/api/users/profile/image",
            headers=auth_header(token),
            data={"image": (io.BytesIO(b"fake-image-data"), "avatar.png")},
            content_type="multipart/form-data",
        )
        self.assertEqual(uploaded.status_code, 200)
        image_url = uploaded.json["data"]["profile_image"]
        self.assertTrue(image_url.startswith("/api/users/profile-images/"))

        served = self.client.get(image_url)
        self.assertEqual(served.status_code, 200)
        served.close()

    def test_profile_image_rejects_unsupported_file(self):
        login = register_and_login_student(self.app, self.client)
        response = self.client.post(
            "/api/users/profile/image",
            headers=auth_header(login["access_token"]),
            data={"image": (io.BytesIO(b"bad"), "avatar.exe")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
