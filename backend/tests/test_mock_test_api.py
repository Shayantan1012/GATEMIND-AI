import unittest

from tests.helpers import (
    auth_header,
    create_and_publish_mock_test,
    create_question,
    make_app,
    register_and_login_admin,
    register_and_login_student,
)


class MockTestApiTest(unittest.TestCase):
    def setUp(self):
        self.app, self.client = make_app()
        self.admin = register_and_login_admin(self.client)
        self.student = register_and_login_student(self.app, self.client)

    def test_list_get_submit_and_history(self):
        question = create_question(self.client, self.admin["access_token"])
        mock_test_id = create_and_publish_mock_test(self.client, self.admin["access_token"], question["question_id"])
        user_headers = auth_header(self.student["access_token"])

        listed = self.client.get("/api/mock-tests", headers=user_headers)
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.json["data"]), 1)

        detail = self.client.get(f"/api/mock-tests/{mock_test_id}", headers=user_headers)
        self.assertEqual(detail.status_code, 200)
        self.assertNotIn("correct_answer", detail.json["data"]["questions"][0])

        submitted = self.client.post(
            f"/api/mock-tests/{mock_test_id}/submit",
            headers=user_headers,
            json={"answers": [{"question_id": question["question_id"], "answer": "4"}]},
        )
        self.assertEqual(submitted.status_code, 200)
        self.assertEqual(submitted.json["data"]["percentage"], 100.0)

        history = self.client.get("/api/mock-tests/history", headers=user_headers)
        self.assertEqual(history.status_code, 200)
        self.assertEqual(len(history.json["data"]), 1)

    def test_wrong_answer_applies_negative_marks(self):
        question = create_question(self.client, self.admin["access_token"])
        mock_test_id = create_and_publish_mock_test(self.client, self.admin["access_token"], question["question_id"])

        submitted = self.client.post(
            f"/api/mock-tests/{mock_test_id}/submit",
            headers=auth_header(self.student["access_token"]),
            json={"answers": [{"question_id": question["question_id"], "answer": "3"}]},
        )
        self.assertEqual(submitted.status_code, 200)
        self.assertEqual(submitted.json["data"]["score"], -0.5)


if __name__ == "__main__":
    unittest.main()
