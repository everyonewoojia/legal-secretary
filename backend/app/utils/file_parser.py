from docx import Document


def parse_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def parse_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def parse_pdf(path: str) -> str:
    raise NotImplementedError("PDF parsing not yet implemented")
