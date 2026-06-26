import os
import uuid

from fastapi import UploadFile

from app.core.config import settings
from app.utils.file_parser import parse_docx, parse_pdf


class FileService:
    @staticmethod
    async def save_upload(file: UploadFile) -> str:
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in (".docx", ".pdf"):
            raise ValueError("Unsupported file format")
        filename = f"{uuid.uuid4().hex}{ext}"
        path = os.path.join(settings.UPLOAD_DIR, filename)
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        content = await file.read()
        with open(path, "wb") as f:
            f.write(content)
        return path

    @staticmethod
    def extract_text(file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".docx":
            return parse_docx(file_path)
        elif ext == ".pdf":
            return parse_pdf(file_path)
        raise ValueError("Unsupported file format")
