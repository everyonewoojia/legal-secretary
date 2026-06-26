from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.core.response import success, error

router = APIRouter(prefix="/api/v1/rag", tags=["rag"])


class SearchRequest(BaseModel):
    query: str
    contract_type: str = ""
    top_k: int = 3


@router.post("/search")
async def rag_search(req: SearchRequest):
    from backend.app.services.rag_service import retrieve
    chunks = await retrieve(req.query, req.contract_type, req.top_k)
    return success({"chunks": chunks})
