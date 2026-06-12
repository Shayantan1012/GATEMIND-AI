from app.models.performance import PerformanceRecord


class MockTestService:
    def __init__(self, questions, performance, evaluator, analyzer, profile_updater):
        self.questions = questions
        self.performance = performance
        self.evaluator = evaluator
        self.analyzer = analyzer
        self.profile_updater = profile_updater

    def list_available(self):
        return self.questions.list_mock_tests(published_only=True)

    def get_test(self, mock_test_id):
        mock_test = self.questions.find_mock_test(mock_test_id)
        if not mock_test or not mock_test.is_published:
            raise ValueError("Mock test not found")
        questions = self.questions.find_questions(question_ids=mock_test.question_ids)
        by_id = {question.question_id: question for question in questions}
        return {"mock_test": mock_test, "questions": [by_id[item].public_dict() for item in mock_test.question_ids if item in by_id]}

    def submit(self, user_id, mock_test_id, answers, time_taken_seconds=0):
        test = self.get_test(mock_test_id)["mock_test"]
        submitted = {str(item.get("question_id")): item.get("answer") for item in answers}
        questions = self.questions.find_questions(question_ids=test.question_ids)
        results = [self.evaluator.evaluate(question, submitted.get(question.question_id)) for question in questions]
        record = PerformanceRecord.create(
            user_id=user_id,
            mock_test_id=mock_test_id,
            score=round(sum(item["awarded_marks"] for item in results), 2),
            total_marks=sum(question.marks for question in questions),
            correct_count=sum(item["correct"] for item in results),
            incorrect_count=sum(item["answered"] and not item["correct"] for item in results),
            unanswered_count=sum(not item["answered"] for item in results),
            subject_breakdown=self.analyzer.analyze(results),
            answers=results,
            mock_test_title=test.title,
            time_taken_seconds=max(0, min(int(time_taken_seconds or 0), test.duration_minutes * 60)),
        )
        self.performance.save(record)
        self.profile_updater.update(user_id, record)
        return record.to_dict()

    def history(self, user_id):
        return self.performance.find_by_user(user_id)
