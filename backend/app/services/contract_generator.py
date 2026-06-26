import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.contract import ContractSession, ContractDraft, ChatMessage
from backend.app.core.llm import llm_complete


async def generate_draft(db: AsyncSession, session_id: int) -> ContractDraft | None:
    result = await db.execute(
        select(ContractSession).where(ContractSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        return None

    slots = json.loads(session.slot_json or "{}")
    if not slots.get("party_a") or not slots.get("party_b"):
        return None

    prompt = (
        f"请根据以下合同要素生成一份规范的{slots.get('contract_type', '合同')}：\n"
        f"甲方：{slots.get('party_a', '')}\n"
        f"乙方：{slots.get('party_b', '')}\n"
        f"标的：{slots.get('subject', '')}\n"
        f"金额：{slots.get('amount', '')}\n"
        f"期限：{slots.get('term', '')}\n"
        f"违约责任：{slots.get('penalty', '')}\n"
        f"请按标准法律合同格式输出，包含条款编号。"
    )
    content = await llm_complete(prompt)

    draft = ContractDraft(
        session_id=session_id,
        version_no=1,
        title=f"{slots.get('contract_type', '合同')}初稿",
        content=content,
    )
    db.add(draft)
    await db.commit()
    await db.refresh(draft)
    return draft
