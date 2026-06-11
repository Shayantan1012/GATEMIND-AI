from abc import ABC, abstractmethod


class EvaluationStrategy(ABC):
    @abstractmethod
    def is_correct(self, expected, actual) -> bool:
        raise NotImplementedError
