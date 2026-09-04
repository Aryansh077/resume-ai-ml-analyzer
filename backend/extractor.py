from pathlib import Path
import fitz
from docx import Document

def extract_text(path: str) -> str:
    p = Path(path)
    suffix = p.suffix.lower()

    if suffix == ".pdf":
        doc = fitz.open(path)
        return "\n".join(page.get_text() for page in doc)

    if suffix == ".docx":
        doc = Document(path)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)

    raise ValueError("Only PDF and DOCX resumes are supported.")
