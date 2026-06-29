import json
import re
from typing import AsyncGenerator

from openai import AsyncOpenAI

from app.core.config import settings

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI | None:
    global _client
    if _client is None and settings.LLM_API_KEY:
        _client = AsyncOpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL)
    return _client


async def chat_stream(messages: list[dict]) -> AsyncGenerator[str, None]:
    client = _get_client()
    if client is None:
        async for chunk in _mock_stream(messages):
            yield chunk
        return
    response = await client.chat.completions.create(
        model=settings.LLM_MODEL_NAME, messages=messages, stream=True,
    )
    async for chunk in response:
        delta = chunk.choices[0].delta if chunk.choices else None
        if delta and delta.content:
            yield delta.content


async def chat_once(messages: list[dict]) -> str:
    client = _get_client()
    if client is None:
        return _mock_chat(messages)
    response = await client.chat.completions.create(
        model=settings.LLM_MODEL_NAME, messages=messages,
    )
    return response.choices[0].message.content or ""


async def chat_once_json(messages: list[dict]) -> dict:
    raw = await chat_once(messages)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        raw = raw.rsplit("\n", 1)[0]
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    return json.loads(raw)


CONTRACT_TEMPLATES = {
    "技术服务合同": """技术服务合同

合同编号：MOCK-2025-TS-001

甲方（委托方）：________________________
乙方（服务方）：________________________

根据《中华人民共和国民法典》及相关法律法规，甲乙双方经平等协商，就技术服务事宜达成如下协议：

第一条 服务内容
1.1 甲方委托乙方提供以下技术服务：________________________
1.2 服务期限：自____年____月____日起至____年____月____日止。
1.3 服务地点：________________________

第二条 服务费用及支付
2.1 本合同总金额为人民币：________________________元（大写：________________________）。
2.2 支付方式：________________________

第三条 双方权利与义务
3.1 甲方应按照约定提供必要的技术资料、数据和工作条件。
3.2 乙方应按照约定的技术标准和质量要求完成服务。

第四条 验收标准
4.1 验收标准：________________________
4.2 验收期限：乙方完成服务后____个工作日内。

第五条 违约责任
5.1 任何一方违反本合同约定，应向对方支付合同总金额____%的违约金。

第六条 保密条款
6.1 双方对在履行本合同过程中知悉的对方商业秘密和技术秘密负有保密义务。
6.2 保密期限自本合同签订之日起____年。

第七条 争议解决
7.1 因本合同引起的争议，双方应友好协商解决。
7.2 协商不成的，任何一方均可向合同签订地人民法院提起诉讼。

甲方（盖章）：________________    乙方（盖章）：________________
日期：____年____月____日          日期：____年____月____日""",

    "采购合同": """采购合同

合同编号：MOCK-2025-PROC-001

甲方（买方）：________________________
乙方（卖方）：________________________

根据《中华人民共和国民法典》及相关法律法规，甲乙双方经平等协商，就货物采购事宜达成如下协议：

第一条 采购标的
1.1 产品名称：________________________
1.2 规格型号：________________________
1.3 数量：________________________
1.4 质量标准：________________________

第二条 合同价款
2.1 总价为人民币：________________________元（大写：________________________）。
2.2 以上价格包含运费、税费等所有费用。

第三条 交付与验收
3.1 交付时间：____年____月____日前。
3.2 交付地点：________________________
3.3 验收期限：甲方收到货物后____个工作日内完成验收。

第四条 付款方式
4.1 合同签订后____个工作日内支付合同总价的____%作为预付款。
4.2 货物验收合格后____个工作日内支付剩余____%。

第五条 质量保证
5.1 乙方保证所供货物为全新、合格产品。
5.2 质保期为验收合格之日起____个月。

第六条 违约责任
6.1 逾期交货：每逾期一日，乙方按合同总价的____%支付违约金。
6.2 逾期付款：每逾期一日，甲方按逾期金额的____%支付违约金。

甲方（盖章）：________________    乙方（盖章）：________________
日期：____年____月____日          日期：____年____月____日""",

    "劳动合同": """劳动合同

合同编号：MOCK-2025-EMP-001

甲方（用人单位）：________________________
乙方（劳动者）：________________________

根据《中华人民共和国劳动法》《中华人民共和国劳动合同法》及相关法律法规，甲乙双方经平等协商，自愿签订本合同。

第一条 合同期限
1.1 本合同期限类型为：________________（固定期限/无固定期限/以完成一定工作任务为期限）。
1.2 试用期自____年____月____日起至____年____月____日止。

第二条 工作内容与地点
2.1 乙方同意在________________岗位工作。
2.2 工作地点：________________________

第三条 工作时间与休息休假
3.1 甲方实行标准工时制，每日工作不超过8小时，每周工作不超过40小时。

第四条 劳动报酬
4.1 乙方月工资为人民币________元（税前）。
4.2 试用期工资为人民币________元，不低于约定工资的80%。

第五条 社会保险与福利
5.1 甲方依法为乙方缴纳养老保险、医疗保险、失业保险、工伤保险和生育保险。

第六条 合同解除与终止
6.1 双方解除或终止劳动合同应按照《劳动合同法》的有关规定执行。

甲方（盖章）：________________    乙方（签字）：________________
日期：____年____月____日          日期：____年____月____日""",

    "合作协议": """合作协议

合同编号：MOCK-2025-COOP-001

甲方：________________________
乙方：________________________

根据《中华人民共和国民法典》及相关法律法规，甲乙双方本着平等互利、诚实信用的原则，就合作事宜达成如下协议：

第一条 合作内容
1.1 双方同意在________________领域开展合作。
1.2 合作期限：自____年____月____日起至____年____月____日止。

第二条 双方权利义务
2.1 甲方权利义务：________________________
2.2 乙方权利义务：________________________

第三条 利益分配
3.1 合作收益按照以下方式分配：________________________

第四条 知识产权
4.1 合作期间产生的知识产权归属：________________________

第五条 保密义务
5.1 双方对合作中知悉的对方商业秘密负有保密义务。

第六条 退出机制
6.1 任何一方提前____日书面通知对方，可解除本协议。

第七条 争议解决
7.1 因本合同引起的争议，双方应友好协商解决。
7.2 协商不成的，提交________________仲裁委员会仲裁。

甲方（盖章）：________________    乙方（盖章）：________________
日期：____年____月____日          日期：____年____月____日""",

    "保密协议": """保密协议

协议编号：MOCK-2025-NDA-001

甲方（信息披露方）：________________________
乙方（信息接收方）：________________________

为保护甲方商业秘密和保密信息，甲乙双方经协商一致，签订本保密协议。

第一条 保密信息范围
1.1 本协议所指保密信息包括：________________________
1.2 保密信息可以书面、口头、电子等形式存在。

第二条 保密义务
2.1 乙方承诺对甲方的保密信息严格保密。

第三条 保密期限
3.1 本协议有效期为自签署之日起____年。

第四条 例外情形
以下信息不属于保密信息：________________________

第五条 违约责任
5.1 乙方违反本协议约定的，应向甲方支付违约金人民币________元。

第六条 争议解决
6.1 因本协议引起的争议，双方应友好协商解决。
6.2 协商不成的，向甲方所在地人民法院提起诉讼。

甲方（盖章）：________________    乙方（盖章）：________________
日期：____年____月____日          日期：____年____月____日""",
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
    {
        "clause_location": "付款条款",
        "risk_type": "付款期限延长",
        "risk_level": "high",
        "description": '对方将付款期限从合同签订后30日延长至90日，且删除了逾期付款的违约金条款。该修改大幅延长了回款周期，增加了资金占用成本，且缺乏对逾期付款的约束机制。',
        "suggestion": "建议话术：我理解贵司需要合理的账期安排，但90天的付款周期确实超出了我们的标准。我们的建议是60天，同时保留逾期付款的违约金条款，这对双方都是公平的保障。",
        "legal_basis": "《民法典》第六百二十八条：买受人应当按照约定的时间支付价款。",
    },
    {
        "clause_location": "违约金上限",
        "risk_type": "违约金比例过低",
        "risk_level": "high",
        "description": "对方新增条款将违约金上限设定为合同总金额的5%，远低于行业惯例的20%-30%。该限制将大大削弱违约条款的约束力。",
        "suggestion": "建议话术：违约金条款的核心功能是保障合同履行，5%的上限在实务中约束力非常有限。根据民法典的规定和司法实践，20%是行业普遍接受的比例。",
        "legal_basis": "《民法典》第五百八十五条：约定的违约金低于造成的损失的，人民法院或者仲裁机构可以根据当事人的请求予以增加。",
    },
    {
        "clause_location": "知识产权归属",
        "risk_type": "知识产权权属不清",
        "risk_level": "medium",
        "description": '对方将"开发过程中产生的知识产权归双方共同所有"改为"归甲方所有"，未对乙方在合作前已有的知识产权进行区分和保护。',
        "suggestion": "建议话术：知识产权条款需要更细致的区分。我们的建议是：项目专门开发的成果归双方共有，各自原有的背景知识产权仍归各自所有。",
        "legal_basis": "《民法典》第八百六十一：委托开发完成的发明创造，除当事人另有约定的以外，申请专利的权利属于研究开发人。",
    },
    {
        "clause_location": "保密期限",
        "risk_type": "保密期限过短",
        "risk_level": "low",
        "description": "对方将保密期限从合同终止后5年缩短为2年。对于涉及核心技术或商业机密的项目，2年的保密期可能不足以保护信息价值。",
        "suggestion": "建议话术：考虑到项目涉及的技术信息具有较长的商业生命周期，我们建议将保密期定为合同终止后3年，这是一个比较平衡的方案。",
        "legal_basis": "《反不正当竞争法》第九条：商业秘密是指不为公众所知悉、具有商业价值并经权利人采取相应保密措施的技术信息、经营信息等商业信息。",
    },
    {
        "clause_location": "争议解决方式",
        "risk_type": "管辖法院变更",
        "risk_level": "medium",
        "description": '对方将争议解决方式从"甲方所在地人民法院诉讼"改为"被告所在地人民法院诉讼"。这一修改会增加我方在对方违约时的维权成本。',
        "suggestion": "建议话术：争议解决条款我们希望保持公平。选择被告所在地诉讼在实践中对守约方不太有利。我们的建议是选择合同签订地作为管辖法院。",
        "legal_basis": "《民事诉讼法》第二十四条：因合同纠纷提起的诉讼，由被告住所地或者合同履行地人民法院管辖。",
    },
]


def _extract_contract_type(messages: list[dict]) -> str:
    for m in messages:
        if m["role"] == "system":
            match = re.search(r"【(.+?)】", m["content"])
            if match:
                return match.group(1)
    return ""


def _extract_slots(text: str) -> dict:
    slots = {}
    for key, regex in SLOT_EXTRACTION_MAP.items():
        match = regex.search(text)
        if match:
            slots[key] = match.group(1).strip()
    return slots


def _infer_field_from_context(messages: list[dict]) -> str | None:
    """Look at the last AI message to infer which field the user is answering."""
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


def _mock_chat(messages: list[dict]) -> str:
    last = messages[-1]["content"] if messages else ""

    if "生成合同" in last or "generate" in last.lower() or "合同生成专家" in last or "输出合同全文" in last:
        type_name = _extract_contract_type(messages)
        return _mock_generate_contract(type_name, messages)

    if "风险" in last or "risk" in last.lower() or "counter-argument" in last.lower() or "谈判" in last:
        if "plan_a" in last or "plan_b" in last or "counter" in last.lower():
            return _mock_counter_argument()
        return _mock_risk_analysis()

    type_name = _extract_contract_type(messages)

    all_slots = _all_slots_from_messages(messages)
    last_slots = _extract_slots(last)

    if not last_slots:
        inferred = _infer_field_from_context(messages)
        if inferred and inferred not in all_slots:
            all_slots[inferred] = last.strip()
            last_slots[inferred] = last.strip()

    filled_set = set(all_slots.keys())
    missing = [f for f in FIELD_LIST if f not in filled_set]

    ack_parts = []
    for k, v in last_slots.items():
        ack_parts.append(f"好的，已记录「{k}：{v}」")
    ack = "，".join(ack_parts) + "。" if ack_parts else ""

    if missing and ack:
        question = FIELD_QUESTIONS.get(missing[0], f"请问{missing[0]}是什么？")
        reply = f"{ack} {question}"
    elif missing:
        reply = FIELD_QUESTIONS.get(missing[0], f"请问{missing[0]}是什么？")
    elif ack:
        reply = f"{ack} 所有合同信息已收集完成！您可以点击「生成合同」按钮来生成合同初稿。"
    else:
        reply = "所有合同信息已收集完成！您可以点击「生成合同」按钮来生成合同初稿。"

    if all_slots:
        return json.dumps({"content": reply, "slots": all_slots}, ensure_ascii=False)
    return reply


def _all_slots_from_messages(messages: list[dict], from_system: bool = False) -> dict:
    all_slots = {}
    for m in messages:
        if m["role"] == "user":
            all_slots.update(_extract_slots(m.get("content", "")))
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


def _fill_placeholders(text: str, slots: dict) -> str:
    for key, value in slots.items():
        v = value.strip('"').strip()
        text = text.replace(f"【{key}】", v)
    if "甲方" in slots:
        a = slots["甲方"].strip('"').strip()
        text = re.sub(r"甲方（[^）]+）[：:]\s*_{2,}", f"甲方：{a}", text)
        text = re.sub(r"甲方[：:]\s*_{2,}", f"甲方：{a}", text)
    if "乙方" in slots:
        b = slots["乙方"].strip('"').strip()
        for pat in [r"乙方（[^）]+）[：:]\s*_{2,}", r"乙方[：:]\s*_{2,}"]:
            text = re.sub(pat, f"乙方：{b}", text)
    if "合同金额" in slots:
        m = slots["合同金额"].strip('"').strip()
        text = re.sub(r"人民币[：:]\s*_{2,}", f"人民币：{m}", text)
        text = re.sub(r"总价为人民币[：:]\s*_{2,}", f"总价为人民币：{m}", text)
    if "交付物" in slots:
        d = slots["交付物"].strip('"').strip()
        text = re.sub(r"1\.1\s*甲方委托乙方提供以下技术服务[：:]\s*_{2,}", f"1.1 甲方委托乙方提供以下技术服务：{d}", text)
        text = re.sub(r"产品名称[：:]\s*_{2,}", f"产品名称：{d}", text)
    if "付款节点" in slots:
        p = slots["付款节点"].strip('"').strip()
        text = re.sub(r"支付方式[：:]\s*_{2,}", f"支付方式：{p}", text)
        text = re.sub(r"2\.2\s*支付方式[：:]\s*_{2,}", f"2.2 支付方式：{p}", text)
    if "验收标准" in slots:
        s = slots["验收标准"].strip('"').strip()
        text = re.sub(r"验收标准[：:]\s*_{2,}", f"验收标准：{s}", text)
        text = re.sub(r"4\.1\s*验收标准[：:]\s*_{2,}", f"4.1 验收标准：{s}", text)
    return text


def _mock_generate_contract(contract_type: str = "", messages: list[dict] = None) -> str:
    for name, template in CONTRACT_TEMPLATES.items():
        if name in contract_type or contract_type in name:
            result = template
            if messages:
                slots = _all_slots_from_messages(messages, from_system=True)
                if slots:
                    result = _fill_placeholders(result, slots)
            return result
    return CONTRACT_TEMPLATES["技术服务合同"]


def _mock_risk_analysis() -> str:
    return json.dumps(MOCK_RISK_ITEMS, ensure_ascii=False)


def _mock_counter_argument() -> str:
    return json.dumps({
        "plan_a": "【强硬方案】根据《民法典》相关规定，原条款对双方权利义务的分配是公平合理的，建议维持原条款不变。如对方坚持修改，我方要求对等调整其他条款以维持合同整体平衡。",
        "plan_b": "【折中方案】建议在原条款基础上进行适当调整，寻求双方均可接受的平衡点。可考虑将争议条款修改为更中立的表述，或增加补充条款以保障双方利益。",
    }, ensure_ascii=False)


async def _mock_stream(messages: list[dict]):
    text = _mock_chat(messages)
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "content" in data:
            yield data
            return
    except (json.JSONDecodeError, TypeError):
        pass
    for char in text:
        yield char
