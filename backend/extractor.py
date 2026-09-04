from pathlib import Path

import fitz

from docx import Document


def extract_pdf_text(
    file_path: str
) -> str:

    text = []

    document = fitz.open(
        file_path
    )

    try:

        for page in document:

            text.append(
                page.get_text()
            )

    finally:

        document.close()


    return "\n".join(text)


def extract_docx_text(
    file_path: str
) -> str:

    document = Document(
        file_path
    )

    text = []

    for paragraph in document.paragraphs:

        if paragraph.text.strip():

            text.append(
                paragraph.text
            )


    return "\n".join(text)


def extract_text(
    file_path: str
) -> str:

    extension = (
        Path(file_path)
        .suffix
        .lower()
    )


    if extension == ".pdf":

        return extract_pdf_text(
            file_path
        )


    if extension == ".docx":

        return extract_docx_text(
            file_path
        )


    raise ValueError(
        "Unsupported file type."
    )