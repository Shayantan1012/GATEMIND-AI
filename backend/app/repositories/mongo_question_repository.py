from app.models.mock_test import MockTest
from app.models.question import Question


class MongoQuestionRepository:
    def __init__(self, db):
        self.questions = db["questions"]
        self.mock_tests = db["mock_tests"]

    def save_question(self, question):
        self.questions.replace_one({"_id": question.question_id}, question.to_dict(), upsert=True)
        return question

    def find_question(self, question_id):
        data = self.questions.find_one({"_id": question_id})
        return Question.from_dict(data) if data else None

    def delete_question(self, question_id):
        result = self.questions.delete_one({"_id": question_id})
        return result.deleted_count > 0

    def find_questions(self, question_ids=None, subject=None):
        query = {}
        if question_ids is not None:
            query["_id"] = {"$in": question_ids}
        if subject:
            query["subject"] = subject
        return [Question.from_dict(data) for data in self.questions.find(query)]

    def save_mock_test(self, test):
        self.mock_tests.replace_one({"_id": test.mock_test_id}, test.to_dict(), upsert=True)
        return test

    def find_mock_test(self, test_id):
        data = self.mock_tests.find_one({"_id": test_id})
        return MockTest.from_dict(data) if data else None

    def delete_mock_test(self, test_id):
        result = self.mock_tests.delete_one({"_id": test_id})
        return result.deleted_count > 0

    def list_mock_tests(self, published_only=True):
        return [MockTest.from_dict(data) for data in self.mock_tests.find({"is_published": True} if published_only else {}).sort("created_at", -1)]

    def count_questions(self):
        return self.questions.count_documents({})

    def count_mock_tests(self):
        return self.mock_tests.count_documents({})
