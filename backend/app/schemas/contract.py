from datetime import datetime

from pydantic import BaseModel, Field


class ContractTypeResponse(BaseModel):
    id: int
    name: str
    code: str
    description: str
    sort_order: int

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str = Field(..., max_length=2000)
    history: list[dict] = []


class ChatResponse(BaseModel):
    reply: str
    is_complete: bool = False
    collected_fields: dict = {}


class GenerateRequest(BaseModel):
    collected_fields: dict
    title: str = ""


class ContractResponse(BaseModel):
    id: int
    title: str
    type_id: int
    status: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ContractListItem(BaseModel):
    id: int
    title: str
    type_name: str | None = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DownloadRequest(BaseModel):
    contract_id: int
    format: str = Field("docx", pattern=r"^(docx|pdf)$")


class CreateContractRequest(BaseModel):
    type_id: int
    title: str = ""
    content: str = ""
