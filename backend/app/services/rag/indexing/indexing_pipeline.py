from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4


class IndexingPipeline(ABC):
    def execute(self, file_path: Path, uploaded_by: str, metadata: dict | None = None) -> dict:
        document_id = str(uuid4())
        documents = self.parse(file_path)
        chunks = self.process(documents)
        return self.store(document_id, file_path, uploaded_by, chunks, metadata or {})

    @abstractmethod
    def parse(self, file_path: Path):
        raise NotImplementedError

    @abstractmethod
    def process(self, documents):
        raise NotImplementedError

    @abstractmethod
    def store(self, document_id, file_path, uploaded_by, chunks, metadata):
        raise NotImplementedError
