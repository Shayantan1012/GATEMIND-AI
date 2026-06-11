from pathlib import Path

from langchain_core.documents import Document

from app.services.rag.parsers.document_parser import DocumentParser


class ImageDocumentParser(DocumentParser):
    def parse(self, file_path: Path) -> list[Document]:
        try:
            import pytesseract
            from PIL import Image

            text = pytesseract.image_to_string(Image.open(file_path))
        except Exception:
            text = f"Image uploaded: {file_path.name}. Configure Pillow and pytesseract for OCR extraction."
        return [Document(page_content=text, metadata={"source": file_path.name, "page_no": 1, "modality": "image"})]
