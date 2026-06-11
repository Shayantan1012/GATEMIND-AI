from app.models.enums import QuestionType
from app.services.mocktest.evaluation_strategies.mcq_evaluation_strategy import MCQEvaluationStrategy
from app.services.mocktest.evaluation_strategies.msq_evaluation_strategy import MSQEvaluationStrategy
from app.services.mocktest.evaluation_strategies.nat_evaluation_strategy import NATEvaluationStrategy


class QuestionEvaluator:
    def __init__(self):
        self.strategies = {
            QuestionType.MCQ: MCQEvaluationStrategy(),
            QuestionType.MSQ: MSQEvaluationStrategy(),
            QuestionType.NAT: NATEvaluationStrategy(),
        }

    def evaluate(self, question, actual_answer) -> dict:
        answered = actual_answer is not None and actual_answer != ""
        correct = answered and self.strategies[question.question_type].is_correct(question.correct_answer, actual_answer)
        marks = question.marks if correct else (-question.negative_marks if answered else 0.0)
        return {
            "question_id": question.question_id,
            "subject": question.subject,
            "answered": answered,
            "correct": correct,
            "awarded_marks": marks,
            "max_marks": question.marks,
            "submitted_answer": actual_answer,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
        }
