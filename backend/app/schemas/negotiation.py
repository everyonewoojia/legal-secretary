from pydantic import BaseModel


class DiffItem(BaseModel):
    type: str
    content: str
    line_number: int | None = None


class DiffResponse(BaseModel):
    original_text: str
    modified_text: str
    changes: list[DiffItem]


class RiskItem(BaseModel):
    id: int
    clause_location: str
    risk_type: str
    risk_level: str
    description: str
    suggestion: str = ""
    legal_basis: str = ""

    class Config:
        from_attributes = True


class CounterArgumentRequest(BaseModel):
    risk_id: int
    negotiation_style: str = "balanced"


class CounterArgumentResponse(BaseModel):
    plan_a: str
    plan_b: str
