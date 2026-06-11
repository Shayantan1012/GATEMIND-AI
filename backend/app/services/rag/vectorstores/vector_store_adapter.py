from abc import ABC, abstractmethod


class VectorStoreAdapter(ABC):
    @abstractmethod
    def add(self, chunks: list[dict]) -> int:
        raise NotImplementedError

    @abstractmethod
    def search(self, query_vector, top_k, filters=None, query_text="") -> list[dict]:
        raise NotImplementedError
