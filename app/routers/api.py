from fastapi import APIRouter

from app.routers import auth, users, contracts, negotiation, rag, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["合同起草"])
api_router.include_router(negotiation.router, prefix="/negotiation", tags=["谈判审查"])
api_router.include_router(rag.router, prefix="/rag", tags=["知识库"])
api_router.include_router(admin.router, prefix="/admin", tags=["后台管理"])


@api_router.get("/health")
def health_check():
    return {"status": "ok"}
