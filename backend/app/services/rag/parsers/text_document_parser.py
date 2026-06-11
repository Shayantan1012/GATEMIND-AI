from pathlib import Path

from langchain_core.documents import Document

from app.services.rag.parsers.document_parser import DocumentParser


class TextDocumentParser(DocumentParser):
    def parse(self, file_path: Path) -> list[Document]:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        return [Document(page_content=text, metadata={"source": file_path.name, "page_no": 1})]
