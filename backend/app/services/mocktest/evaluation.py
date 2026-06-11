from abc import ABC, abstractmethod
from math import isclose

from app.models.enums import QuestionType


class EvaluationStrategy(ABC):
    @abstractmethod
    def is_correct(self, expected, actual) -> bool:
        raise NotImplementedError


class MCQEvaluationStrategy(EvaluationStrategy):
    def is_correct(self, expected, actual) -> bool:
        return str(expected).strip() == str(actual).strip()


class MSQEvaluationStrategy(EvaluationStrategy):
    def is_correct(self, expected, actual) -> bool:
        expected_values = expected if isinstance(expected, list) else [expected]
        actual_values = actual if isinstance(actual, list) else [actual]
        return {str(value).strip() for value in expected_values} == {
            str(value).strip() for value in actual_values
        }


class NATEvaluationStrategy(EvaluationStrategy):
    def is_correct(self, expected, actual) -> bool:
        try:
            if isinstance(expected, list) and len(expected) == 2:
                return float(expected[0]) <= float(actual) <= float(expected[1])
            return isclose(float(expected), float(actual), rel_tol=1e-6, abs_tol=1e-3)
        except (TypeError, ValueError):
            return False


class QuestionEvaluator:
    def __init__(self):
        self.strategies = {
            QuestionType.MCQ: MCQEvaluationStrategy(),
            QuestionType.MSQ: MSQEvaluationStrategy(),
            QuestionType.NAT: NATEvaluationStrategy(),
        }

    def evaluate(self, question, actual_answer) -> dict:
        answered = actual_answer is not None and actual_answer != ""
        correct = answered and self.strategies[question.question_type].is_correct(
            question.correct_answer,
            actual_answer,
        )
        awarded_marks = question.marks if correct else (-question.negative_marks if answered else 0.0)
        return {
            "question_id": question.question_id,
            "subject": question.subject,
            "answered": answered,
            "correct": correct,
            "awarded_marks": awarded_marks,
            "max_marks": question.marks,
            "submitted_answer": actual_answer,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
        }
