from pydantic import BaseModel


class Response(BaseModel):
    code: int = 0
    message: str = "ok"
    data: object | None = None


class PageParams(BaseModel):
    page: int = 1
    page_size: int = 20


class PageResult(BaseModel):
    total: int
    page: int
    page_size: int
    items: list
