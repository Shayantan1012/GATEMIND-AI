from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.models.citation import Citation


@dataclass
class RAGResponse:
    answer: str
    citations: list[Citation]
    query_type: str = "TEXT"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "answer": self.answer,
            "citations": [citation.to_dict() for citation in self.citations],
            "query_type": self.query_type,
            "created_at": self.created_at.isoformat(),
        }
