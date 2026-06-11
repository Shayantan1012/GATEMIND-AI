from app.models.mock_test import MockTest
from app.models.performance import PerformanceRecord
from app.models.question import QuestionFactory


class QuestionBankService:
    def __init__(self, repository):
        self.repository = repository

    def create_question(self, data: dict, admin_id: str):
        required = ["question_type", "prompt", "subject", "correct_answer"]
        missing = [key for key in required if data.get(key) is None]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        return self.repository.save_question(QuestionFactory.create(data, admin_id))

    def list_questions(self, subject: str | None = None):
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


class PerformanceAnalyzer:
    def analyze(self, results: list[dict]) -> dict:
        breakdown = {}
        for result in results:
            subject = result["subject"]
            item = breakdown.setdefault(
                subject,
                {"score": 0.0, "total_marks": 0.0, "correct": 0, "incorrect": 0, "unanswered": 0},
            )
            item["score"] += result["awarded_marks"]
            item["total_marks"] += result["max_marks"]
            if not result["answered"]:
                item["unanswered"] += 1
            elif result["correct"]:
                item["correct"] += 1
            else:
                item["incorrect"] += 1
        for item in breakdown.values():
            item["percentage"] = (
                round(max(item["score"], 0) / item["total_marks"] * 100, 2)
                if item["total_marks"]
                else 0.0
            )
        return breakdown


class PersonalizedRAGUpdater:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def update(self, user_id: str, record: PerformanceRecord) -> None:
        user = self.user_repository.find_by_id(user_id)
        if not user or not user.user_profile:
            return
        profile = user.user_profile
        profile.performance_percentage = record.percentage
        profile.overall_progress = max(profile.overall_progress, record.percentage)
        profile.preparation_progress = min(100.0, profile.preparation_progress + 2.0)
        profile.mock_test_history.append(
            {
                "performance_id": record.performance_id,
                "mock_test_id": record.mock_test_id,
                "score": record.score,
                "total_marks": record.total_marks,
                "percentage": record.percentage,
                "attempted_at": record.attempted_at.isoformat(),
            }
        )
        self.user_repository.update(user)


class MockTestService:
    def __init__(self, question_repository, performance_repository, evaluator, analyzer, profile_updater):
        self.questions = question_repository
        self.performance = performance_repository
        self.evaluator = evaluator
        self.analyzer = analyzer
        self.profile_updater = profile_updater

    def list_available(self):
        return self.questions.list_mock_tests(published_only=True)

    def get_test(self, mock_test_id: str) -> dict:
        mock_test = self.questions.find_mock_test(mock_test_id)
        if not mock_test or not mock_test.is_published:
            raise ValueError("Mock test not found")
        questions = self.questions.find_questions(question_ids=mock_test.question_ids)
        by_id = {question.question_id: question for question in questions}
        return {
            "mock_test": mock_test,
            "questions": [by_id[item].public_dict() for item in mock_test.question_ids if item in by_id],
        }

    def submit(self, user_id: str, mock_test_id: str, answers: list[dict]) -> dict:
        test_data = self.get_test(mock_test_id)
        submitted = {str(item.get("question_id")): item.get("answer") for item in answers}
        questions = self.questions.find_questions(question_ids=test_data["mock_test"].question_ids)
        results = [self.evaluator.evaluate(question, submitted.get(question.question_id)) for question in questions]
        total_marks = sum(question.marks for question in questions)
        score = round(sum(result["awarded_marks"] for result in results), 2)
        record = PerformanceRecord.create(
            user_id=user_id,
            mock_test_id=mock_test_id,
            score=score,
            total_marks=total_marks,
            correct_count=sum(result["correct"] for result in results),
            incorrect_count=sum(result["answered"] and not result["correct"] for result in results),
            unanswered_count=sum(not result["answered"] for result in results),
            subject_breakdown=self.analyzer.analyze(results),
            answers=results,
        )
        self.performance.save(record)
        self.profile_updater.update(user_id, record)
        return record.to_dict()

    def history(self, user_id: str) -> list[dict]:
        return self.performance.find_by_user(user_id)
