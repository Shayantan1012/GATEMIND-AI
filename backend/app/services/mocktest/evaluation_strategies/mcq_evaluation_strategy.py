from app.services.mocktest.evaluation_strategies.evaluation_strategy import EvaluationStrategy


class MCQEvaluationStrategy(EvaluationStrategy):
    def is_correct(self, expected, actual) -> bool:
        return str(expected).strip() == str(actual).strip()
