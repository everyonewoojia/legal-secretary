from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    contract_type: str = Field(..., description="合同类型编码")


class ChatRequest(BaseModel):
    session_id: int
    message: str = Field(..., max_length=2000)


class GenerateRequest(BaseModel):
    session_id: int
    format: str = "docx"


class ExportRequest(BaseModel):
    draft_id: int
    format: str = "docx"


class NegotiateRequest(BaseModel):
    draft_id: int
    modified_text: str = ""
    contract_type: str = ""
