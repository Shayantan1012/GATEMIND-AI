from pathlib import Path

from app.services.rag.parsers.image_document_parser import ImageDocumentParser
from app.services.rag.parsers.pdf_document_parser import PDFDocumentParser
from app.services.rag.parsers.text_document_parser import TextDocumentParser


class DocumentParserFactory:
    PARSERS = {
        ".pdf": PDFDocumentParser,
        ".txt": TextDocumentParser,
        ".md": TextDocumentParser,
        ".csv": TextDocumentParser,
        ".json": TextDocumentParser,
        ".png": ImageDocumentParser,
        ".jpg": ImageDocumentParser,
        ".jpeg": ImageDocumentParser,
        ".webp": ImageDocumentParser,
    }

    @classmethod
    def create(cls, file_path: Path):
        parser_class = cls.PARSERS.get(file_path.suffix.lower())
        if not parser_class:
            raise ValueError(f"Unsupported document type: {file_path.suffix}")
        return parser_class()
