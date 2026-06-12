import unittest
import io

from tests.helpers import (
    auth_header,
    make_app,
    register_and_login_admin,
    register_and_login_student,
    upload_text_document,
)


class RagApiTest(unittest.TestCase):
    def setUp(self):
        self.app, self.client = make_app()
        self.admin = register_and_login_admin(self.client)
        self.student = register_and_login_student(self.app, self.client)

    def test_document_upload_list_chat_and_history(self):
        uploaded = upload_text_document(self.client, self.admin["access_token"])
        self.assertEqual(uploaded.status_code, 201)
        self.assertGreater(uploaded.json["data"]["chunk_count"], 0)

        documents = self.client.get("/api/admin/rag/documents", headers=auth_header(self.admin["access_token"]))
        self.assertEqual(documents.status_code, 200)
        self.assertEqual(len(documents.json["data"]), 1)

        chat = self.client.post(
            "/api/rag/chat",
            headers=auth_header(self.student["access_token"]),
            json={"query": "What does BIRCH build?"},
        )
        self.assertEqual(chat.status_code, 200)
        self.assertTrue(chat.json["data"]["citations"])

        history = self.client.get("/api/rag/history", headers=auth_header(self.student["access_token"]))
        self.assertEqual(history.status_code, 200)
        self.assertEqual(len(history.json["data"]), 1)

    def test_empty_rag_query_returns_400(self):
        response = self.client.post(
            "/api/rag/chat",
            headers=auth_header(self.student["access_token"]),
            json={"query": ""},
        )
        self.assertEqual(response.status_code, 400)

    def test_unsupported_document_type_returns_400(self):
        response = self.client.post(
            "/api/admin/rag/documents",
            headers=auth_header(self.admin["access_token"]),
            data={"file": (io.BytesIO(b"bad"), "bad.exe")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_user_can_upload_multiple_files_and_query_attached_documents(self):
        uploaded = self.client.post(
            "/api/rag/documents",
            headers=auth_header(self.student["access_token"]),
            data={
                "files": [
                    (io.BytesIO(b"BIRCH builds a clustering feature tree."), "birch.txt"),
                    (io.BytesIO(b"K-means requires a chosen number of clusters."), "kmeans.txt"),
                ]
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(uploaded.status_code, 201)
        self.assertEqual(len(uploaded.json["data"]), 2)

        documents = self.client.get("/api/rag/documents", headers=auth_header(self.student["access_token"]))
        self.assertEqual(documents.status_code, 200)
        self.assertEqual(len(documents.json["data"]), 2)

        selected_id = uploaded.json["data"][0]["_id"]
        chat = self.client.post(
            "/api/rag/chat",
            headers=auth_header(self.student["access_token"]),
            json={"query": "What does BIRCH build?", "filters": {"document_ids": [selected_id]}},
        )
        self.assertEqual(chat.status_code, 200)
        self.assertTrue(chat.json["data"]["citations"])
        self.assertTrue(all(item["document_id"] == selected_id for item in chat.json["data"]["citations"]))

    def test_user_cannot_query_another_users_attached_document(self):
        uploaded = self.client.post(
            "/api/rag/documents",
            headers=auth_header(self.student["access_token"]),
            data={"files": [(io.BytesIO(b"Private notes"), "private.txt")]},
            content_type="multipart/form-data",
        )
        document_id = uploaded.json["data"][0]["_id"]
        other = register_and_login_student(self.app, self.client, email="other@example.com")

        response = self.client.post(
            "/api/rag/chat",
            headers=auth_header(other["access_token"]),
            json={"query": "Read private notes", "filters": {"document_ids": [document_id]}},
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
