"""Mock 数据与回退逻辑，当 LLM_API_KEY 未配置时使用"""

import json
import re
from typing import AsyncGenerator

CONTRACT_TEMPLATES = {
    "技术服务合同": """技术服务合同\n\n合同编号：MOCK-2025-TS-001\n\n甲方（委托方）：________________________\n乙方（服务方）：________________________\n\n根据《中华人民共和国民法典》及相关法律法规，甲乙双方经平等协商，就技术服务事宜达成如下协议：\n\n第一条 服务内容\n1.1 甲方委托乙方提供以下技术服务：________________________\n1.2 服务期限：自____年____月____日起至____年____月____日止。\n\n第二条 服务费用及支付\n2.1 本合同总金额为人民币：________________________元。\n2.2 支付方式：________________________\n\n第三条 双方权利与义务\n3.1 甲方应按照约定提供必要的技术资料、数据和工作条件。\n3.2 乙方应按照约定的技术标准和质量要求完成服务。\n\n第四条 验收标准\n4.1 验收标准：________________________\n\n第五条 违约责任\n5.1 任何一方违反本合同约定，应向对方支付合同总金额____%的违约金。\n\n第六条 保密条款\n6.1 双方对在履行本合同过程中知悉的对方商业秘密和技术秘密负有保密义务。\n\n第七条 争议解决\n7.1 因本合同引起的争议，双方应友好协商解决。\n7.2 协商不成的，任何一方均可向合同签订地人民法院提起诉讼。\n\n甲方（盖章）：________________    乙方（盖章）：________________\n日期：____年____月____日          日期：____年____月____日""",
    "采购合同": """采购合同\n\n合同编号：MOCK-2025-PROC-001\n\n甲方（买方）：________________________\n乙方（卖方）：________________________\n\n根据《中华人民共和国民法典》及相关法律法规，甲乙双方经平等协商，就货物采购事宜达成如下协议：\n\n第一条 采购标的\n1.1 产品名称：________________________\n1.2 规格型号：________________________\n1.3 数量：________________________\n\n第二条 合同价款\n2.1 总价为人民币：________________________元。\n2.2 以上价格包含运费、税费等所有费用。\n\n第三条 交付与验收\n3.1 交付时间：____年____月____日前。\n3.2 交付地点：________________________\n\n第四条 付款方式\n4.1 合同签订后____个工作日内支付合同总价的____%作为预付款。\n\n第五条 质量保证\n5.1 乙方保证所供货物为全新、合格产品。\n5.2 质保期为验收合格之日起____个月。\n\n第六条 违约责任\n6.1 逾期交货：每逾期一日，乙方按合同总价的____%支付违约金。\n\n甲方（盖章）：________________    乙方（盖章）：________________\n日期：____年____月____日          日期：____年____月____日""",
    "劳动合同": """劳动合同\n\n合同编号：MOCK-2025-EMP-001\n\n甲方（用人单位）：________________________\n乙方（劳动者）：________________________\n\n根据《中华人民共和国劳动法》《中华人民共和国劳动合同法》及相关法律法规，甲乙双方经平等协商，自愿签订本合同。\n\n第一条 合同期限\n1.1 本合同期限自____年____月____日起至____年____月____日止。\n1.2 试用期自____年____月____日起至____年____月____日止。\n\n第二条 工作内容与地点\n2.1 乙方同意在________________岗位工作。\n\n第三条 劳动报酬\n3.1 乙方月工资为人民币________元（税前）。\n\n第四条 社会保险与福利\n4.1 甲方依法为乙方缴纳养老保险、医疗保险、失业保险、工伤保险和生育保险。\n\n第五条 合同解除与终止\n5.1 双方解除或终止劳动合同应按照《劳动合同法》的有关规定执行。\n\n甲方（盖章）：________________    乙方（签字）：________________\n日期：____年____月____日          日期：____年____月____日""",
    "合作协议": """合作协议\n\n合同编号：MOCK-2025-COOP-001\n\n甲方：________________________\n乙方：________________________\n\n根据《中华人民共和国民法典》及相关法律法规，甲乙双方本着平等互利、诚实信用的原则，就合作事宜达成如下协议：\n\n第一条 合作内容\n1.1 双方同意在________________领域开展合作。\n1.2 合作期限：自____年____月____日起至____年____月____日止。\n\n第二条 利益分配\n2.1 合作收益按照以下方式分配：________________________\n\n第三条 知识产权\n3.1 合作期间产生的知识产权归属：________________________\n\n第四条 保密义务\n4.1 双方对合作中知悉的对方商业秘密负有保密义务。\n\n第五条 退出机制\n5.1 任何一方提前____日书面通知对方，可解除本协议。\n\n第六条 争议解决\n6.1 因本合同引起的争议，双方应友好协商解决。\n\n甲方（盖章）：________________    乙方（盖章）：________________\n日期：____年____月____日          日期：____年____月____日""",
    "保密协议": """保密协议\n\n协议编号：MOCK-2025-NDA-001\n\n甲方（信息披露方）：________________________\n乙方（信息接收方）：________________________\n\n为保护甲方商业秘密和保密信息，甲乙双方经协商一致，签订本保密协议。\n\n第一条 保密信息范围\n1.1 本协议所指保密信息包括：________________________\n\n第二条 保密义务\n2.1 乙方承诺对甲方的保密信息严格保密。\n\n第三条 保密期限\n3.1 本协议有效期为自签署之日起____年。\n\n第四条 违约责任\n4.1 乙方违反本协议约定的，应向甲方支付违约金人民币________元。\n\n第五条 争议解决\n5.1 因本协议引起的争议，双方应友好协商解决。\n\n甲方（盖章）：________________    乙方（盖章）：________________\n日期：____年____月____日          日期：____年____月____日""",
}

FIELD_QUESTIONS = {
    "甲方": "请问甲方（委托方/购买方）的公司全称是什么？",
    "乙方": "请问乙方（受托方/销售方）的公司全称是什么？",
    "合同金额": "请问合同总金额是多少？",
    "交付物": "请问具体的服务内容或交付物是什么？",
    "付款节点": "请问您希望如何安排付款方式？是一次性付清还是分阶段付款？",
    "验收标准": "请问验收标准是什么？需要达到哪些具体指标？",
    "违约责任": "关于违约责任，您认为违约金比例设定为多少比较合理？",
    "保密期限": "请问保密期限约定为几年比较合适？",
}
QUESTION_TO_FIELD = {v: k for k, v in FIELD_QUESTIONS.items()}
FIELD_LIST = ["甲方", "乙方", "合同金额", "交付物", "付款节点", "验收标准", "违约责任", "保密期限"]

SLOT_EXTRACTION_MAP = {
    "甲方": re.compile(r"(?:甲方|委托方|购买方|采购方|买方|我们|我公司|我方)[：:是叫]?\s*([^\n，,。.]+)"),
    "乙方": re.compile(r"(?:乙方|受托方|销售方|卖方|对方|贵司|你们)[：:是叫]?\s*([^\n，,。.]+)"),
    "合同金额": re.compile(r"(?:合同)?(?:金额|总价|价款|费用)[：:是叫]?\s*([0-9，,.\d]+[万亿元]*)"),
    "交付物": re.compile(r"(?:交付物|服务内容|服务范围|工作内容|项目内容|开发内容|货物名称|交付|提供)[：:是叫]?\s*([^\n，,。.]+)"),
    "付款节点": re.compile(r"(?:付款|支付)(?:方式|节点|条件|比例)[：:是叫]?\s*([^\n，,。.]+)"),
    "验收标准": re.compile(r"(?:验收|交付)(?:标准|方式|条件|指标)[：:是叫]?\s*([^\n，,。.]+)"),
    "违约责任": re.compile(r"(?:违约|赔偿)(?:责任|条款|金比例)[：:是叫]?\s*([^\n，,。.]+)"),
    "保密期限": re.compile(r"(?:保密|保密期限)[：:是叫]?\s*([^\n，,。.]+)"),
}

MOCK_RISK_ITEMS = [
    {"clause_location": "付款条款", "risk_type": "付款期限延长", "risk_level": "high", "description": "对方将付款期限从30日延长至90日，且删除了逾期付款的违约金条款。", "suggestion": "建议将付款期限缩短至60日并保留违约金条款。", "legal_basis": "《民法典》第六百二十八条：买受人应当按照约定的时间支付价款。"},
    {"clause_location": "违约金上限", "risk_type": "违约金比例过低", "risk_level": "high", "description": "对方将违约金上限设定为合同总金额的5%，远低于行业惯例的20%-30%。", "suggestion": "建议将违约金上限提升至合同总金额的20%。", "legal_basis": "《民法典》第五百八十五条：约定的违约金低于造成的损失的，人民法院可以根据当事人的请求予以增加。"},
    {"clause_location": "知识产权归属", "risk_type": "知识产权权属不清", "risk_level": "medium", "description": "对方将项目成果的知识产权改为归其单方所有。", "suggestion": "建议约定项目成果知识产权归双方共有，背景知识产权归各自所有。", "legal_basis": "《民法典》第八百六十一：委托开发完成的发明创造，除当事人另有约定的以外，申请专利的权利属于研究开发人。"},
    {"clause_location": "保密期限", "risk_type": "保密期限过短", "risk_level": "low", "description": "对方将保密期限从合同终止后5年缩短为2年。", "suggestion": "建议将保密期限恢复至合同终止后3年。", "legal_basis": "《反不正当竞争法》第九条：商业秘密是指不为公众所知悉、具有商业价值并经权利人采取相应保密措施的信息。"},
    {"clause_location": "争议解决方式", "risk_type": "管辖法院变更", "risk_level": "medium", "description": "对方将争议管辖法院改为被告所在地法院。", "suggestion": "建议选择合同签订地或原告所在地法院作为管辖法院。", "legal_basis": "《民事诉讼法》第二十四条：因合同纠纷提起的诉讼，由被告住所地或者合同履行地人民法院管辖。"},
]


def extract_contract_type(messages: list[dict]) -> str:
    for m in messages:
        if m["role"] == "system":
            match = re.search(r"【(.+?)】", m["content"])
            if match:
                return match.group(1)
    return ""


def extract_slots(text: str) -> dict:
    slots = {}
    for key, regex in SLOT_EXTRACTION_MAP.items():
        match = regex.search(text)
        if match:
            slots[key] = match.group(1).strip()
    return slots


def infer_field_from_context(messages: list[dict]) -> str | None:
    for m in reversed(messages[:-1]):
        if m["role"] in ("assistant", "agent"):
            for q_text, field in QUESTION_TO_FIELD.items():
                if q_text in m.get("content", ""):
                    return field
            for field in FIELD_LIST:
                if f"请问{field}" in m.get("content", ""):
                    return field
            break
    return None


def all_slots_from_messages(messages: list[dict], from_system: bool = False) -> dict:
    all_slots = {}
    for m in messages:
        if m["role"] == "user":
            all_slots.update(extract_slots(m.get("content", "")))
        elif from_system and m["role"] == "system":
            js_match = re.search(r'收集的要素.*?(\{.+?\})', m["content"], re.DOTALL)
            if js_match:
                try:
                    data = json.loads(js_match.group(1))
                    if isinstance(data, dict):
                        all_slots.update({k: str(v).strip('"') for k, v in data.items()})
                except (json.JSONDecodeError, AttributeError):
                    pass
    return all_slots


def fill_placeholders(text: str, slots: dict) -> str:
    for key, value in slots.items():
        v = value.strip('"').strip()
        text = text.replace(f"【{key}】", v)
    for key, pats in [("甲方", [r"甲方（[^）]+）[：:]\s*_{2,}", r"甲方[：:]\s*_{2,}"]),
                       ("乙方", [r"乙方（[^）]+）[：:]\s*_{2,}", r"乙方[：:]\s*_{2,}"]),
                       ("合同金额", [r"总价为人民币[：:]\s*_{2,}", r"人民币[：:]\s*_{2,}"]),
                       ("交付物", [r"产品名称[：:]\s*_{2,}", r"1\.1\s*甲方委托乙方提供以下技术服务[：:]\s*_{2,}"]),
                       ("付款节点", [r"2\.2\s*支付方式[：:]\s*_{2,}", r"支付方式[：:]\s*_{2,}"]),
                       ("验收标准", [r"验收标准[：:]\s*_{2,}", r"4\.1\s*验收标准[：:]\s*_{2,}"])]:
        if key in slots:
            v = slots[key].strip('"').strip()
            for pat in pats:
                text = re.sub(pat, f"{pat.split(r'[：:]')[0] if pat.count(r'[') > 0 else key}：{v}", text)
    return text


def mock_chat(messages: list[dict]) -> str:
    last = messages[-1]["content"] if messages else ""
    if "生成合同" in last or "generate" in last.lower() or "合同生成专家" in last or "输出合同全文" in last:
        type_name = extract_contract_type(messages)
        return mock_generate_contract(type_name, messages)
    if "风险" in last or "risk" in last.lower():
        if "plan_a" in last or "counter" in last.lower():
            return mock_counter_argument()
        return mock_risk_analysis()
    type_name = extract_contract_type(messages)
    all_slots = all_slots_from_messages(messages)
    last_slots = extract_slots(last)
    if not last_slots:
        inferred = infer_field_from_context(messages)
        if inferred and inferred not in all_slots:
            all_slots[inferred] = last.strip()
            last_slots[inferred] = last.strip()
    filled_set = set(all_slots.keys())
    missing = [f for f in FIELD_LIST if f not in filled_set]
    ack_parts = [f"好的，已记录「{k}：{v}」" for k, v in last_slots.items()]
    ack = "，".join(ack_parts) + "。" if ack_parts else ""
    if missing:
        question = FIELD_QUESTIONS.get(missing[0], f"请问{missing[0]}是什么？")
        reply = f"{ack} {question}" if ack else question
    elif ack:
        reply = f"{ack} 所有合同信息已收集完成！您可以点击「生成合同」按钮来生成合同初稿。"
    else:
        reply = "所有合同信息已收集完成！您可以点击「生成合同」按钮来生成合同初稿。"
    if all_slots:
        return json.dumps({"content": reply, "slots": all_slots}, ensure_ascii=False)
    return reply


def mock_generate_contract(contract_type: str = "", messages: list[dict] = None) -> str:
    for name, template in CONTRACT_TEMPLATES.items():
        if name in contract_type or contract_type in name:
            result = template
            if messages:
                slots = all_slots_from_messages(messages, from_system=True)
                if slots:
                    result = fill_placeholders(result, slots)
            return result
    return CONTRACT_TEMPLATES["技术服务合同"]


def mock_risk_analysis() -> str:
    return json.dumps(MOCK_RISK_ITEMS, ensure_ascii=False)


def mock_counter_argument() -> str:
    return json.dumps({"plan_a": "【强硬方案】建议维持原条款不变。如对方坚持修改，我方要求对等调整其他条款以维持合同整体平衡。", "plan_b": "【折中方案】建议在原条款基础上进行适当调整，寻求双方均可接受的平衡点。"}, ensure_ascii=False)


async def mock_stream(messages: list[dict]):
    text = mock_chat(messages)
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "content" in data:
            for char in data["content"]:
                yield char
            return
    except (json.JSONDecodeError, TypeError):
        pass
    for char in text:
        yield char
