from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader

from app.services.rag.parsers.document_parser import DocumentParser


class PDFDocumentParser(DocumentParser):
    def parse(self, file_path: Path) -> list[Document]:
        reader = PdfReader(str(file_path))
        return [
            Document(
                page_content=page.extract_text() or "",
                metadata={"source": file_path.name, "page_no": index + 1},
            )
            for index, page in enumerate(reader.pages)
        ]
