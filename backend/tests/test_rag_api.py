import unittest
import io
from pathlib import Path
from tempfile import TemporaryDirectory

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
        self.assertEqual(uploaded.json["data"]["description"], "Clustering notes")

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

    def test_admin_can_delete_indexed_document(self):
        uploaded = upload_text_document(self.client, self.admin["access_token"])
        self.assertEqual(uploaded.status_code, 201)
        document_id = uploaded.json["data"]["_id"]

        deleted = self.client.delete(
            f"/api/admin/rag/documents/{document_id}",
            headers=auth_header(self.admin["access_token"]),
        )
        self.assertEqual(deleted.status_code, 200)

        documents = self.client.get("/api/admin/rag/documents", headers=auth_header(self.admin["access_token"]))
        self.assertEqual(documents.status_code, 200)
        self.assertEqual(len(documents.json["data"]), 0)

    def test_empty_rag_query_returns_400(self):
        response = self.client.post(
            "/api/rag/chat",
            headers=auth_header(self.student["access_token"]),
            json={"query": ""},
        )
        self.assertEqual(response.status_code, 400)

    def test_user_can_create_switch_and_delete_conversations(self):
        headers = auth_header(self.student["access_token"])
        first = self.client.post("/api/rag/conversations", headers=headers, json={"title": "BIRCH study"})
        second = self.client.post("/api/rag/conversations", headers=headers, json={"title": "Networks study"})
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        first_id = first.json["data"]["conversation_id"]
        second_id = second.json["data"]["conversation_id"]

        first_chat = self.client.post(
            "/api/rag/chat",
            headers=headers,
            json={"conversation_id": first_id, "query": "Explain BIRCH"},
        )
        second_chat = self.client.post(
            "/api/rag/chat",
            headers=headers,
            json={"conversation_id": second_id, "query": "Explain TCP"},
        )
        self.assertEqual(first_chat.status_code, 200)
        self.assertEqual(second_chat.status_code, 200)
        self.assertEqual(first_chat.json["data"]["conversation"]["conversation_id"], first_id)

        conversations = self.client.get("/api/rag/conversations", headers=headers)
        self.assertEqual(conversations.status_code, 200)
        self.assertEqual(len(conversations.json["data"]), 2)

        first_messages = self.client.get(f"/api/rag/conversations/{first_id}/messages", headers=headers)
        second_messages = self.client.get(f"/api/rag/conversations/{second_id}/messages", headers=headers)
        self.assertEqual([item["query"] for item in first_messages.json["data"]], ["Explain BIRCH"])
        self.assertEqual([item["query"] for item in second_messages.json["data"]], ["Explain TCP"])

        deleted = self.client.delete(f"/api/rag/conversations/{first_id}", headers=headers)
        self.assertEqual(deleted.status_code, 200)
        missing = self.client.get(f"/api/rag/conversations/{first_id}/messages", headers=headers)
        self.assertEqual(missing.status_code, 404)

    def test_deleting_conversation_deletes_attached_user_documents_and_files(self):
        with TemporaryDirectory() as temporary_directory:
            self.app.config["UPLOAD_FOLDER"] = temporary_directory
            self.app.extensions["services"]["rag_chat"].upload_folder = Path(temporary_directory)
            headers = auth_header(self.student["access_token"])
            conversation = self.client.post("/api/rag/conversations", headers=headers, json={"title": "Attached notes"})
            conversation_id = conversation.json["data"]["conversation_id"]
            uploaded = self.client.post(
                "/api/rag/documents",
                headers=headers,
                data={"files": [(io.BytesIO(b"SD index compares scatter and separation."), "sd-index.txt")]},
                content_type="multipart/form-data",
            )
            self.assertEqual(uploaded.status_code, 201)
            document = uploaded.json["data"][0]
            document_id = document["_id"]
            uploaded_file = Path(temporary_directory) / "users" / self.student["user"]["user_id"] / document["source"]
            self.assertTrue(uploaded_file.exists())

            chat = self.client.post(
                "/api/rag/chat",
                headers=headers,
                json={
                    "conversation_id": conversation_id,
                    "query": "What does the SD index compare?",
                    "filters": {"document_ids": [document_id]},
                },
            )
            self.assertEqual(chat.status_code, 200)
            self.assertTrue(self.app.extensions["services"]["rag_repo"].find_document(document_id))
            self.assertTrue(self.app.extensions["services"]["rag_repo"].list_chunks({"document_id": document_id}))

            deleted = self.client.delete(f"/api/rag/conversations/{conversation_id}", headers=headers)
            self.assertEqual(deleted.status_code, 200)
            self.assertIsNone(self.app.extensions["services"]["rag_repo"].find_document(document_id))
            self.assertEqual(self.app.extensions["services"]["rag_repo"].list_chunks({"document_id": document_id}), [])
            self.assertFalse(uploaded_file.exists())

    def test_deleting_conversation_deletes_selected_unqueried_documents(self):
        with TemporaryDirectory() as temporary_directory:
            self.app.config["UPLOAD_FOLDER"] = temporary_directory
            self.app.extensions["services"]["rag_chat"].upload_folder = Path(temporary_directory)
            headers = auth_header(self.student["access_token"])
            conversation = self.client.post("/api/rag/conversations", headers=headers, json={"title": "Unasked upload"})
            conversation_id = conversation.json["data"]["conversation_id"]
            uploaded = self.client.post(
                "/api/rag/documents",
                headers=headers,
                data={"files": [(io.BytesIO(b"Uploaded but not queried yet."), "unused.txt")]},
                content_type="multipart/form-data",
            )
            document = uploaded.json["data"][0]
            document_id = document["_id"]
            uploaded_file = Path(temporary_directory) / "users" / self.student["user"]["user_id"] / document["source"]
            self.assertTrue(uploaded_file.exists())

            deleted = self.client.delete(
                f"/api/rag/conversations/{conversation_id}",
                headers=headers,
                json={"document_ids": [document_id]},
            )
            self.assertEqual(deleted.status_code, 200)
            self.assertIsNone(self.app.extensions["services"]["rag_repo"].find_document(document_id))
            self.assertFalse(uploaded_file.exists())

    def test_deleting_conversation_keeps_admin_documents_and_chunks(self):
        uploaded = upload_text_document(self.client, self.admin["access_token"])
        self.assertEqual(uploaded.status_code, 201)
        document_id = uploaded.json["data"]["_id"]
        headers = auth_header(self.student["access_token"])
        conversation = self.client.post("/api/rag/conversations", headers=headers, json={"title": "Admin notes"})
        conversation_id = conversation.json["data"]["conversation_id"]

        chat = self.client.post(
            "/api/rag/chat",
            headers=headers,
            json={
                "conversation_id": conversation_id,
                "query": "What does BIRCH build?",
                "filters": {"document_ids": [document_id]},
            },
        )
        self.assertEqual(chat.status_code, 400)

        deleted = self.client.delete(
            f"/api/rag/conversations/{conversation_id}",
            headers=headers,
            json={"document_ids": [document_id]},
        )
        self.assertEqual(deleted.status_code, 200)
        self.assertIsNotNone(self.app.extensions["services"]["rag_repo"].find_document(document_id))
        self.assertTrue(self.app.extensions["services"]["rag_repo"].list_chunks({"document_id": document_id}))

    def test_user_cannot_access_another_users_conversation(self):
        headers = auth_header(self.student["access_token"])
        created = self.client.post("/api/rag/conversations", headers=headers, json={"title": "Private chat"})
        conversation_id = created.json["data"]["conversation_id"]
        other = register_and_login_student(self.app, self.client, email="conversation-other@example.com")
        response = self.client.get(
            f"/api/rag/conversations/{conversation_id}/messages",
            headers=auth_header(other["access_token"]),
        )
        self.assertEqual(response.status_code, 404)

    def test_follow_up_uses_selected_conversation_context(self):
        headers = auth_header(self.student["access_token"])
        created = self.client.post("/api/rag/conversations", headers=headers, json={"title": "Follow-up context"})
        conversation_id = created.json["data"]["conversation_id"]

        first = self.client.post(
            "/api/rag/chat",
            headers=headers,
            json={"conversation_id": conversation_id, "query": "Remember that my focus is graph algorithms."},
        )
        self.assertEqual(first.status_code, 200)

        follow_up = self.client.post(
            "/api/rag/chat",
            headers=headers,
            json={"conversation_id": conversation_id, "query": "What is my focus?"},
        )
        self.assertEqual(follow_up.status_code, 200)
        self.assertIn("graph algorithms", follow_up.json["data"]["answer"])

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
