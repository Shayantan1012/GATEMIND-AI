from pymongo.database import Database

from app.models.admin import Admin
from app.models.mock_test import MockTest
from app.models.question import Question


class MongoAdminRepository:
    def __init__(self, db: Database):
        self.collection = db["admins"]
        self.collection.create_index("email", unique=True)
        self.collection.create_index("sessions.refresh_token")

    def save(self, admin: Admin) -> Admin:
        self.collection.replace_one({"_id": admin.admin_id}, admin.to_dict(), upsert=True)
        return admin

    def update(self, admin: Admin) -> Admin:
        return self.save(admin)

    def find_by_id(self, admin_id: str) -> Admin | None:
        data = self.collection.find_one({"_id": admin_id})
        return Admin.from_dict(data) if data else None

    def find_by_email(self, email: str) -> Admin | None:
        data = self.collection.find_one({"email": email.strip().lower()})
        return Admin.from_dict(data) if data else None

    def find_by_refresh_token(self, refresh_token: str) -> Admin | None:
        data = self.collection.find_one({"sessions.refresh_token": refresh_token})
        return Admin.from_dict(data) if data else None

    def exists_by_email(self, email: str) -> bool:
        return self.collection.count_documents({"email": email.strip().lower()}, limit=1) > 0

    def count(self) -> int:
        return self.collection.count_documents({})


class MongoQuestionRepository:
    def __init__(self, db: Database):
        self.questions = db["questions"]
        self.mock_tests = db["mock_tests"]
        self.questions.create_index([("subject", 1), ("question_type", 1)])
        self.mock_tests.create_index("is_published")

    def save_question(self, question: Question) -> Question:
        self.questions.replace_one({"_id": question.question_id}, question.to_dict(), upsert=True)
        return question

    def find_question(self, question_id: str) -> Question | None:
        data = self.questions.find_one({"_id": question_id})
        return Question.from_dict(data) if data else None

    def find_questions(self, question_ids: list[str] | None = None, subject: str | None = None) -> list[Question]:
        query = {}
        if question_ids is not None:
            query["_id"] = {"$in": question_ids}
        if subject:
            query["subject"] = subject
        return [Question.from_dict(data) for data in self.questions.find(query)]

    def save_mock_test(self, mock_test: MockTest) -> MockTest:
        self.mock_tests.replace_one({"_id": mock_test.mock_test_id}, mock_test.to_dict(), upsert=True)
        return mock_test

    def find_mock_test(self, mock_test_id: str) -> MockTest | None:
        data = self.mock_tests.find_one({"_id": mock_test_id})
        return MockTest.from_dict(data) if data else None

    def list_mock_tests(self, published_only: bool = True) -> list[MockTest]:
        query = {"is_published": True} if published_only else {}
        return [MockTest.from_dict(data) for data in self.mock_tests.find(query).sort("created_at", -1)]

    def count_questions(self) -> int:
        return self.questions.count_documents({})

    def count_mock_tests(self) -> int:
        return self.mock_tests.count_documents({})


class MongoPerformanceRepository:
    def __init__(self, db: Database):
        self.collection = db["performance_records"]
        self.collection.create_index([("user_id", 1), ("attempted_at", -1)])
        self.collection.create_index("mock_test_id")

    def save(self, record) -> dict:
        data = record.to_dict() if hasattr(record, "to_dict") else record
        self.collection.replace_one({"_id": data["_id"]}, data, upsert=True)
        return data

    def find_by_user(self, user_id: str, limit: int = 100) -> list[dict]:
        return list(self.collection.find({"user_id": user_id}).sort("attempted_at", -1).limit(limit))

    def aggregate_user(self, user_id: str) -> dict:
        records = self.find_by_user(user_id)
        if not records:
            return {"attempts": 0, "average_percentage": 0.0, "best_percentage": 0.0}
        percentages = [float(item.get("percentage", 0)) for item in records]
        return {
            "attempts": len(records),
            "average_percentage": round(sum(percentages) / len(percentages), 2),
            "best_percentage": round(max(percentages), 2),
        }

    def count(self) -> int:
        return self.collection.count_documents({})


class MongoRAGRepository:
    def __init__(self, db: Database):
        self.documents = db["rag_documents"]
        self.chunks = db["rag_chunks"]
        self.chats = db["rag_chats"]
        self.documents.create_index("uploaded_at")
        self.chunks.create_index([("document_id", 1), ("chunk_index", 1)])
        self.chats.create_index([("user_id", 1), ("created_at", -1)])

    def save_document(self, document: dict) -> dict:
        self.documents.replace_one({"_id": document["_id"]}, document, upsert=True)
        return document

    def save_chunks(self, chunks: list[dict]) -> int:
        if chunks:
            self.chunks.insert_many(chunks)
        return len(chunks)

    def list_chunks(self, filters: dict | None = None) -> list[dict]:
        return list(self.chunks.find(filters or {}))

    def list_documents(self, limit: int = 100) -> list[dict]:
        return list(self.documents.find().sort("uploaded_at", -1).limit(limit))

    def save_chat(self, chat: dict) -> dict:
        self.chats.insert_one(chat)
        return chat

    def list_chats(self, user_id: str, limit: int = 50) -> list[dict]:
        return list(self.chats.find({"user_id": user_id}).sort("created_at", -1).limit(limit))

    def count_documents(self) -> int:
        return self.documents.count_documents({})


class MongoAuditRepository:
    def __init__(self, db: Database):
        self.collection = db["audit_logs"]
        self.collection.create_index([("actor_id", 1), ("created_at", -1)])

    def save(self, event: dict) -> dict:
        self.collection.insert_one(event)
        return event
