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
        prepared = self._prepare_mock_test_payload(data, admin_id)
        return self.repository.save_mock_test(MockTest.create(prepared, admin_id))

    def list_mock_tests(self):
        return self.repository.list_mock_tests(published_only=False)

    def update_mock_test(self, mock_test_id: str, data: dict, admin_id: str):
        mock_test = self.repository.find_mock_test(mock_test_id)
        if not mock_test:
            raise ValueError("Mock test not found")

        merged_input = {
            "title": data.get("title", mock_test.title),
            "description": data.get("description", mock_test.description),
            "duration_minutes": data.get("duration_minutes", mock_test.duration_minutes),
            "is_published": data.get("is_published", mock_test.is_published),
        }
        if "questions" in data:
            merged_input["questions"] = data.get("questions", [])
        else:
            merged_input["question_ids"] = data.get("question_ids", mock_test.question_ids)
        prepared = self._prepare_mock_test_payload(merged_input, admin_id, existing_question_ids=mock_test.question_ids)

        stale_question_ids = set(mock_test.question_ids) - set(prepared["question_ids"])
        for question_id in stale_question_ids:
            self._delete_inline_question(question_id)

        mock_test.title = prepared["title"].strip()
        mock_test.description = prepared.get("description", "").strip()
        mock_test.question_ids = list(prepared["question_ids"])
        mock_test.duration_minutes = int(prepared["duration_minutes"])
        mock_test.is_published = bool(prepared.get("is_published", mock_test.is_published))
        return self.repository.save_mock_test(mock_test)

    def publish_mock_test(self, mock_test_id: str):
        mock_test = self.repository.find_mock_test(mock_test_id)
        if not mock_test:
            raise ValueError("Mock test not found")
        mock_test.is_published = True
        return self.repository.save_mock_test(mock_test)

    def delete_mock_test(self, mock_test_id: str):
        mock_test = self.repository.find_mock_test(mock_test_id)
        if not mock_test:
            raise ValueError("Mock test not found")
        for question_id in mock_test.question_ids:
            self._delete_inline_question(question_id)
        self.repository.delete_mock_test(mock_test_id)
        return True

    def get_mock_test_questions(self, mock_test) -> list:
        return self.repository.find_questions(question_ids=list(mock_test.question_ids))

    def _prepare_mock_test_payload(self, data: dict, admin_id: str, existing_question_ids: list[str] | None = None):
        title = str(data.get("title", "")).strip()
        if not title:
            raise ValueError("title is required")
        duration = int(data.get("duration_minutes", 60))
        if duration <= 0:
            raise ValueError("duration_minutes must be greater than 0")
        question_ids = []
        if "questions" in data:
            inline_questions = data.get("questions", [])
            if not inline_questions:
                raise ValueError("questions are required")
            existing_lookup = {}
            if existing_question_ids:
                existing_questions = self.repository.find_questions(question_ids=list(existing_question_ids))
                existing_lookup = {question.question_id: question for question in existing_questions}
            for item in inline_questions:
                question = self._save_inline_question(item, admin_id, existing_lookup)
                question_ids.append(question.question_id)
        else:
            if not data.get("question_ids"):
                raise ValueError("question_ids are required")
            question_ids = list(dict.fromkeys(data["question_ids"]))
            questions = self.repository.find_questions(question_ids=question_ids)
            if len(questions) != len(question_ids):
                raise ValueError("One or more question_ids do not exist")
        return {
            "title": title,
            "description": str(data.get("description", "")).strip(),
            "duration_minutes": duration,
            "is_published": bool(data.get("is_published", False)),
            "question_ids": question_ids,
        }

    def _save_inline_question(self, item: dict, admin_id: str, existing_lookup: dict):
        normalized = self._normalize_question_payload(item)
        question_id = normalized.get("question_id")
        if question_id and question_id in existing_lookup:
            question = existing_lookup[question_id]
            question.question_type = question.question_type.__class__(normalized["question_type"])
            question.prompt = normalized["prompt"]
            question.subject = normalized["subject"]
            question.marks = normalized["marks"]
            question.negative_marks = normalized["negative_marks"]
            question.correct_answer = normalized["correct_answer"]
            question.options = normalized["options"]
            question.explanation = normalized["explanation"]
            question.source = normalized["source"]
            question.created_by = admin_id
            return self.repository.save_question(question)
        return self.repository.save_question(QuestionFactory.create(normalized, admin_id))

    def _normalize_question_payload(self, item: dict) -> dict:
        required = ["question_type", "prompt", "subject", "correct_answer"]
        missing = [key for key in required if item.get(key) in (None, "", [])]
        if missing:
            raise ValueError(f"Missing required question fields: {', '.join(missing)}")

        question_type = str(item.get("question_type", "MCQ")).upper()
        options = [str(option).strip() for option in item.get("options", []) if str(option).strip()]
        if question_type in {"MCQ", "MSQ"} and len(options) < 2:
            raise ValueError("MCQ and MSQ questions require at least two options")
                                                                
        correct_answer = item.get("correct_answer")
        if question_type == "MSQ":
            if not isinstance(correct_answer, list) or not correct_answer:
                raise ValueError("MSQ questions require one or more correct answers")
            correct_answer = [str(answer).strip() for answer in correct_answer if str(answer).strip()]
        elif question_type == "MCQ":
            correct_answer = str(correct_answer).strip()
        else:
            correct_answer = str(correct_answer).strip()

        return {
            "question_id": item.get("question_id"),
            "question_type": question_type,
            "prompt": str(item.get("prompt", "")).strip(),
            "subject": str(item.get("subject", "")).strip(),
            "marks": float(item.get("marks", 1)),
            "negative_marks": float(item.get("negative_marks", 0)),
            "correct_answer": correct_answer,
            "options": options,
            "explanation": str(item.get("explanation", "")).strip(),
            "source": str(item.get("source") or "Mock Test Builder").strip(),
        }

    def _delete_inline_question(self, question_id: str):
        question = self.repository.find_question(question_id)
        if question and question.source:
            self.repository.delete_question(question_id)
