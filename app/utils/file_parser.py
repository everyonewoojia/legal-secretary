from docx import Document


def parse_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def parse_pdf(path: str) -> str:
    raise NotImplementedError("PDF parsing not yet implemented")
