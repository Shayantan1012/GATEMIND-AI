from abc import ABC, abstractmethod
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader


class DocumentParser(ABC):
    @abstractmethod
    def parse(self, file_path: Path) -> list[Document]:
        raise NotImplementedError


class TextDocumentParser(DocumentParser):
    def parse(self, file_path: Path) -> list[Document]:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        return [Document(page_content=text, metadata={"source": file_path.name, "page_no": 1})]


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


class ImageDocumentParser(DocumentParser):
    def parse(self, file_path: Path) -> list[Document]:
        text = ""
        try:
            import pytesseract
            from PIL import Image

            text = pytesseract.image_to_string(Image.open(file_path))
        except Exception:
            text = f"Image uploaded: {file_path.name}. Configure Pillow and pytesseract for OCR extraction."
        return [
            Document(
                page_content=text,
                metadata={"source": file_path.name, "page_no": 1, "modality": "image"},
            )
        ]


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
    def create(cls, file_path: Path) -> DocumentParser:
        parser_class = cls.PARSERS.get(file_path.suffix.lower())
        if not parser_class:
            raise ValueError(f"Unsupported document type: {file_path.suffix}")
        return parser_class()


class ChunkingStrategy(ABC):
    @abstractmethod
    def split(self, documents: list[Document]) -> list[Document]:
        raise NotImplementedError


class RecursiveChunkingStrategy(ChunkingStrategy):
    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True,
        )

    def split(self, documents: list[Document]) -> list[Document]:
        return self.splitter.split_documents(documents)
