import json
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.llm import llm_complete
from backend.app.models.contract import RiskItem


async def analyze_risks(
    db: AsyncSession, case_id: int, diff_json: str, contract_type: str
) -> list[dict]:
    prompt = (
        f"你是一名法务专家，请分析以下合同修改内容中的法律风险。\n"
        f"合同类型：{contract_type}\n"
        f"修改内容：{diff_json}\n"
        f"请按JSON数组格式输出风险项，每个风险项包含："
        f"clause_title(条款名), risk_level(high/medium/low), risk_desc(风险描述), advice(建议)"
    )
    result = await llm_complete(prompt)

    risks = []
    try:
        items = json.loads(result)
        for item in items:
            risk = RiskItem(
                case_id=case_id,
                clause_title=item.get("clause_title", ""),
                risk_level=item.get("risk_level", "low"),
                risk_desc=item.get("risk_desc", ""),
                advice=item.get("advice", ""),
            )
            db.add(risk)
            risks.append({
                "clause_title": risk.clause_title,
                "risk_level": risk.risk_level,
                "risk_desc": risk.risk_desc,
                "advice": risk.advice,
            })
        await db.commit()
    except json.JSONDecodeError:
        risk = RiskItem(
            case_id=case_id,
            clause_title="AI解析异常",
            risk_level="unknown",
            risk_desc="大模型返回格式异常，请人工审查",
            advice="请人工审查合同修改内容",
        )
        db.add(risk)
        await db.commit()
        risks.append({
            "clause_title": risk.clause_title,
            "risk_level": risk.risk_level,
            "risk_desc": risk.risk_desc,
            "advice": risk.advice,
        })

    return risks
