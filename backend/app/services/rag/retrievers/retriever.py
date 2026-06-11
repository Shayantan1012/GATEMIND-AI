from abc import ABC, abstractmethod


class Retriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, filters: dict | None = None) -> list[dict]:
        raise NotImplementedError
