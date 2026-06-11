from app.services.mocktest.evaluation_strategies.evaluation_strategy import EvaluationStrategy


class MSQEvaluationStrategy(EvaluationStrategy):
    def is_correct(self, expected, actual) -> bool:
        expected_values = expected if isinstance(expected, list) else [expected]
        actual_values = actual if isinstance(actual, list) else [actual]
        return {str(value).strip() for value in expected_values} == {str(value).strip() for value in actual_values}
