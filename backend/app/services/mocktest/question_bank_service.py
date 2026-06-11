from app.models.mock_test import MockTest
from app.models.question_factory import QuestionFactory


class QuestionBankService:
    def __init__(self, repository):
        self.repository = repository

    def create_question(self, data: dict, admin_id: str):
        required = ["question_type", "prompt", "subject", "correct_answer"]
        missing = [key for key in required if data.get(key) is None]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        return self.repository.save_question(QuestionFactory.create(data, admin_id))

    def list_questions(self, subject=None):
        return self.repository.find_questions(subject=subject)

    def create_mock_test(self, data: dict, admin_id: str):
        if not data.get("title") or not data.get("question_ids"):
            raise ValueError("title and question_ids are required")
        questions = self.repository.find_questions(question_ids=list(data["question_ids"]))
        if len(questions) != len(set(data["question_ids"])):
            raise ValueError("One or more question_ids do not exist")
        return self.repository.save_mock_test(MockTest.create(data, admin_id))

    def publish_mock_test(self, mock_test_id: str):
        mock_test = self.repository.find_mock_test(mock_test_id)
        if not mock_test:
            raise ValueError("Mock test not found")
        mock_test.is_published = True
        return self.repository.save_mock_test(mock_test)
