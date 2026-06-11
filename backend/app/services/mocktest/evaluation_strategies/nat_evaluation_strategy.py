from math import isclose

from app.services.mocktest.evaluation_strategies.evaluation_strategy import EvaluationStrategy


class NATEvaluationStrategy(EvaluationStrategy):
    def is_correct(self, expected, actual) -> bool:
        try:
            if isinstance(expected, list) and len(expected) == 2:
                return float(expected[0]) <= float(actual) <= float(expected[1])
            return isclose(float(expected), float(actual), rel_tol=1e-6, abs_tol=1e-3)
        except (TypeError, ValueError):
            return False
