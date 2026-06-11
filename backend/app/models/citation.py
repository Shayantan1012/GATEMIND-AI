from dataclasses import dataclass


@dataclass
class Citation:
    document_id: str
    source: str
    page_no: int | None = None
    chunk_id: str | None = None

    def to_dict(self):
        return {"document_id": self.document_id, "source": self.source, "page_no": self.page_no, "chunk_id": self.chunk_id}
