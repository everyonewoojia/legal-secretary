import os
import uuid

from fastapi import UploadFile, HTTPException

from app.core.config import settings
from app.utils.file_parser import parse_docx, parse_pdf, parse_txt

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class FileService:
    @staticmethod
    async def save_upload(file: UploadFile) -> str:
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in (".docx", ".pdf", ".txt"):
            raise HTTPException(status_code=400, detail="不支持的文件格式，仅支持 .docx .pdf .txt")

        filename = f"{uuid.uuid4().hex}{ext}"
        path = os.path.join(settings.UPLOAD_DIR, filename)
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        total = 0
        with open(path, "wb") as f:
            while chunk := await file.read(64 * 1024):
                total += len(chunk)
                if total > MAX_FILE_SIZE:
                    f.close()
                    os.remove(path)
                    raise HTTPException(status_code=400, detail="文件大小超过 10MB 限制")
                f.write(chunk)
        return path

    @staticmethod
    def extract_text(file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".docx":
            return parse_docx(file_path)
        elif ext == ".pdf":
            return parse_pdf(file_path)
        elif ext == ".txt":
            return parse_txt(file_path)
        raise ValueError("Unsupported file format")
