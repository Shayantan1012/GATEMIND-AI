from abc import ABC, abstractmethod
from pathlib import Path

from langchain_core.documents import Document


class DocumentParser(ABC):
    @abstractmethod
    def parse(self, file_path: Path) -> list[Document]:
        raise NotImplementedError
