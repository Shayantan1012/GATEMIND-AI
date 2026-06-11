from abc import ABC, abstractmethod

from langchain_core.documents import Document


class ChunkingStrategy(ABC):
    @abstractmethod
    def split(self, documents: list[Document]) -> list[Document]:
        raise NotImplementedError
