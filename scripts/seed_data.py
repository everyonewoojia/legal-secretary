from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.contract_type import ContractType
from app.models.api_key import ApiKeyConfig
from app.models.template import ContractTemplate
from app.models.user import User


def seed():
    db = SessionLocal()

    if db.query(ContractType).count() > 0:
        db.close()
        return

    contract_types = [
        ContractType(name="技术服务合同", code="tech_service", description="适用于软件开发、技术咨询等服务场景", sort_order=1),
        ContractType(name="采购合同", code="procurement", description="适用于商品或原材料采购场景", sort_order=2),
        ContractType(name="劳动合同", code="labor", description="适用于企业与员工建立劳动关系", sort_order=3),
        ContractType(name="合作协议", code="cooperation", description="适用于企业间业务合作场景", sort_order=4),
        ContractType(name="保密协议", code="nda", description="适用于商业秘密保护场景", sort_order=5),
    ]
    db.add_all(contract_types)
    db.flush()

    admin = User(
        phone="13800000000",
        nickname="管理员",
        role="admin",
        company_name="武汉学链科技有限公司",
        hashed_password=hash_password("admin123"),
        is_active=True,
        is_verified=True,
    )
    db.add(admin)

    api_key_config = ApiKeyConfig(
        provider="通义千问",
        api_key="",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_name="qwen-max",
    )
    db.add(api_key_config)

    template_structure = """{ "clauses": ["party_info", "recitals", "definitions", "subject", "payment", "term", "termination", "confidentiality", "liability", "force_majeure", "dispute", "notice", "signature"] }"""

    for ct in contract_types:
        tmpl = ContractTemplate(
            name=f"{ct.name}标准模板",
            type_id=ct.id,
            description=f"{ct.name}的标准合同模板",
            structure=template_structure,
            version="V1.0",
        )
        db.add(tmpl)

    db.commit()
    db.close()
    print("Seed data created successfully")


if __name__ == "__main__":
    seed()
