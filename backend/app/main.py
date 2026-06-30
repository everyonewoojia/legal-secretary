from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.base import Base
from app.core.database import engine, SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.contract_type import ContractType
from app.routers import api_router

Base.metadata.create_all(bind=engine)


def seed_data():
    from datetime import datetime, timezone
    db: Session = SessionLocal()
    try:
        if not db.query(User).first():
            demo_date = datetime(2026, 6, 30, tzinfo=timezone.utc)
            db.add_all([
                User(
                    phone="13800000000",
                    nickname="管理员",
                    role="admin",
                    hashed_password=hash_password("admin1234"),
                    is_verified=True,
                    created_at=demo_date,
                ),
                User(
                    phone="13800000001",
                    nickname="普通用户",
                    role="user",
                    hashed_password=hash_password("user1234"),
                    is_verified=True,
                    created_at=demo_date,
                ),
            ])
        if not db.query(ContractType).first():
            db.add_all([
                ContractType(name="技术服务合同", code="tech_service", description="适用于软件开发、技术咨询等服务", sort_order=1),
                ContractType(name="采购合同", code="procurement", description="适用于货物、设备等采购", sort_order=2),
                ContractType(name="劳动合同", code="employment", description="适用于用人单位与劳动者签订", sort_order=3),
                ContractType(name="合作协议", code="cooperation", description="适用于双方或多方合作", sort_order=4),
                ContractType(name="保密协议", code="non_disclosure", description="适用于商业秘密保护", sort_order=5),
            ])
        db.commit()
    finally:
        db.close()


seed_data()

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

import os
static_dir = os.path.join(settings.UPLOAD_DIR, "avatars")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=settings.UPLOAD_DIR), name="static")


@app.get("/")
def root():
    return {"message": f"{settings.PROJECT_NAME} is running"}
