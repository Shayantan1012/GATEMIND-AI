from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Citation:
    document_id: str
    source: str
    page_no: int | None = None
    chunk_id: str | None = None

    def to_dict(self) -> dict:
        return {
            "document_id": self.document_id,
            "source": self.source,
            "page_no": self.page_no,
            "chunk_id": self.chunk_id,
        }


@dataclass
class RAGResponse:
    answer: str
    citations: list[Citation]
    query_type: str = "TEXT"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "citations": [citation.to_dict() for citation in self.citations],
            "query_type": self.query_type,
            "created_at": self.created_at.isoformat(),
        }
