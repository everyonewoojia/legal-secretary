from pydantic import BaseModel


class SuccessResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: dict | list | None = None


class ErrorResponse(BaseModel):
    code: int
    message: str
    data: dict | list | None = None
