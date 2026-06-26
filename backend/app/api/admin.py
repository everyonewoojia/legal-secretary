from fastapi import APIRouter

from backend.app.core.response import success

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/users")
async def list_users():
    return success({"users": []})


@router.post("/users/{user_id}/audit")
async def audit_user(user_id: int, action: str, reason: str = ""):
    return success({"user_id": user_id, "status": "approved" if action == "approve" else "rejected"})


@router.get("/logs")
async def get_logs(level: str = "", start: str = "", end: str = ""):
    return success({"logs": []})


@router.post("/llm-config")
async def update_llm_config(provider: str, api_key: str):
    return success({"provider": provider, "status": "configured"})
