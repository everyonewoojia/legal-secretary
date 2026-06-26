from datetime import datetime

from pydantic import BaseModel, Field


class LawArticleCreate(BaseModel):
    title: str = Field(..., max_length=128)
    source: str = Field("", max_length=64)
    content: str
    category: str = Field("", max_length=32)


class LawArticleUpdate(BaseModel):
    title: str | None = None
    source: str | None = None
    content: str | None = None
    category: str | None = None


class LawArticleResponse(BaseModel):
    id: int
    title: str
    source: str
    content: str
    category: str
    created_at: datetime

    class Config:
        from_attributes = True


class TemplateCreate(BaseModel):
    name: str = Field(..., max_length=64)
    type_id: int
    description: str = ""
    structure: str


class TemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    structure: str | None = None
    is_active: bool | None = None


class TemplateResponse(BaseModel):
    id: int
    name: str
    type_id: int
    description: str
    version: str
    is_active: bool

    class Config:
        from_attributes = True
