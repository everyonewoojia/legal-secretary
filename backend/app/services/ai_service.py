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


async def chat_stream(messages: list[dict], temperature: float | None = None) -> AsyncGenerator[str, None]:
    client = _get_client()
    if client is None:
        async for chunk in _mock_stream(messages):
            yield chunk
        return
    kwargs = dict(model=settings.LLM_MODEL_NAME, messages=messages, stream=True)
    if temperature is not None:
        kwargs["temperature"] = temperature
    response = await client.chat.completions.create(**kwargs)
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


_COMMON_PREAMBLE = """\
合同编号：{number}

甲方：________________________
乙方：________________________

根据《中华人民共和国民法典》及相关法律法规，甲乙双方经平等协商，就{subject}事宜达成如下协议：

"""

CONTRACT_TEMPLATES = {
    "技术服务合同": """技术服务合同

""" + _COMMON_PREAMBLE.format(number="MOCK-2025-TS-001", subject="技术服务") + """\
第一条 合同标的
1.1 甲方委托乙方提供以下技术服务：________________________
1.2 服务期限：自____年____月____日起至____年____月____日止。

第二条 价款与支付
2.1 本合同总金额为人民币：________________________元（大写：________________________）。
2.2 支付方式：________________________

第三条 双方权利义务
3.1 甲方应按照约定提供必要的技术资料、数据和工作条件。
3.2 乙方应按照约定的技术标准和质量要求完成服务。
3.3 验收标准：________________________
3.4 验收期限：乙方完成服务后____个工作日内。

第四条 违约责任
4.1 任何一方违反本合同约定，应向对方支付合同总金额____%的违约金。

第五条 保密
5.1 双方对在履行本合同过程中知悉的对方商业秘密和技术秘密负有保密义务。
5.2 保密期限自本合同签订之日起____年。

第六条 争议解决
6.1 因本合同引起的争议，双方应友好协商解决。
6.2 协商不成的，任何一方均可向合同签订地人民法院提起诉讼。

甲方（盖章）：________________    乙方（盖章）：________________
日期：____年____月____日          日期：____年____月____日""",

    "采购合同": """采购合同

""" + _COMMON_PREAMBLE.format(number="MOCK-2025-PROC-001", subject="货物采购") + """\
第一条 合同标的
1.1 产品名称：________________________
1.2 规格型号：________________________
1.3 数量：________________________
1.4 质量标准：________________________

第二条 价款与支付
2.1 总价为人民币：________________________元（大写：________________________）。
2.2 以上价格包含运费、税费等所有费用。
2.3 合同签订后____个工作日内支付合同总价的____%作为预付款。
2.4 货物验收合格后____个工作日内支付剩余____%。

第三条 双方权利义务
3.1 乙方应按照约定时间交付货物，甲方应及时验收。
3.2 交付时间：____年____月____日前。
3.3 交付地点：________________________
3.4 验收期限：甲方收到货物后____个工作日内完成验收。

第四条 违约责任
4.1 逾期交货：每逾期一日，乙方按合同总价的____%支付违约金。
4.2 逾期付款：每逾期一日，甲方按逾期金额的____%支付违约金。

第五条 质量保证
5.1 乙方保证所供货物为全新、合格产品。
5.2 质保期为验收合格之日起____个月。

第六条 争议解决
6.1 因本合同引起的争议，双方应友好协商解决。
6.2 协商不成的，任何一方均可向合同签订地人民法院提起诉讼。

甲方（盖章）：________________    乙方（盖章）：________________
日期：____年____月____日          日期：____年____月____日""",

    "劳动合同": """劳动合同

甲方（用人单位）：________________________
法定代表人：________________________
住所地：________________________

乙方（劳动者）：________________________
身份证号码：________________________
住址：________________________
联系电话：________________________

根据《中华人民共和国劳动法》《中华人民共和国劳动合同法》及相关法律法规，甲乙双方经平等协商，自愿签订本合同，共同遵守。

第一条 合同期限
1.1 本合同期限类型为：________________（固定期限/无固定期限/以完成一定工作任务为期限）。
1.2 固定期限合同：自____年____月____日起至____年____月____日止。
1.3 试用期自____年____月____日起至____年____月____日止，试用期为____个月。
1.4 试用期工资为人民币________元/月，不低于约定工资的80%。

第二条 工作内容与工作地点
2.1 乙方同意在________________岗位工作，具体职责为：________________________。
2.2 工作地点为：________________________
2.3 甲方根据工作需要，经与乙方协商一致，可对工作岗位和地点进行合理调整。

第三条 工作时间与休息休假
3.1 甲方实行________________工时制度。
3.2 每日工作时间不超过8小时，每周工作时间不超过40小时。
3.3 加班规则：________________________
3.4 乙方依法享有法定节假日、年休假、病假等休假权利。

第四条 劳动报酬
4.1 乙方月工资为人民币________元（税前），其中基本工资________元，绩效工资________元。
4.2 加班费计算基数为人民币________元/月。
4.3 甲方于每月____日以________方式支付上月工资。

第五条 社会保险与福利待遇
5.1 甲方依法为乙方缴纳养老保险、医疗保险、失业保险、工伤保险、生育保险（五险）。
5.2 社会保险自____年____月起开始缴纳。
5.3 其他福利待遇：________________________

第六条 劳动保护与职业危害防护
6.1 甲方应为乙方提供符合国家规定的劳动安全卫生条件和必要的劳动保护用品。
6.2 甲方应按规定对乙方进行安全生产教育和培训。
6.3 对从事有职业危害作业的乙方，甲方应定期进行健康检查。

第七条 劳动纪律与规章制度
7.1 乙方应遵守甲方依法制定的各项规章制度。
7.2 甲方应将规章制度公示或以书面形式告知乙方。

第八条 竞业限制与培训服务期
8.1 竞业限制约定：________________________
8.2 服务期约定：________________________
8.3 培训违约金：________________________

第九条 合同解除与终止
9.1 甲乙双方解除或终止本合同，应按照《劳动合同法》的有关规定执行。
9.2 经济补偿按国家有关规定执行。

第十条 争议解决
10.1 因本合同发生的劳动争议，双方应协商解决。
10.2 协商不成的，可向________________劳动争议仲裁委员会申请仲裁。
10.3 对仲裁裁决不服的，可依法向人民法院提起诉讼。

第十一条 附则
11.1 本合同一式两份，甲乙双方各执一份，具有同等法律效力。
11.2 本合同自甲乙双方签字盖章之日起生效。

甲方（盖章）：________________    乙方（签字）：________________
日期：____年____月____日          日期：____年____月____日""",

    "合作协议": """合作协议

""" + _COMMON_PREAMBLE.format(number="MOCK-2025-COOP-001", subject="合作") + """\
第一条 合同标的
1.1 双方同意在________________领域开展合作。
1.2 合作期限：自____年____月____日起至____年____月____日止。

第二条 价款与支付
3.1 合作收益按照以下方式分配：________________________

第三条 双方权利义务
3.1 甲方权利义务：________________________
3.2 乙方权利义务：________________________
3.3 合作期间产生的知识产权归属：________________________

第四条 违约责任
4.1 任何一方违反本协议约定，应向对方承担违约责任。
4.2 任何一方提前____日书面通知对方，可解除本协议。

第五条 保密
5.1 双方对合作中知悉的对方商业秘密负有保密义务。

第六条 争议解决
6.1 因本协议引起的争议，双方应友好协商解决。
6.2 协商不成的，提交________________仲裁委员会仲裁。

甲方（盖章）：________________    乙方（盖章）：________________
日期：____年____月____日          日期：____年____月____日""",

    "保密协议": """保密协议

协议编号：MOCK-2025-NDA-001

甲方（信息披露方）：________________________
乙方（信息接收方）：________________________

根据《中华人民共和国民法典》及相关法律法规，甲乙双方经平等协商，就保密事宜达成如下协议：

第一条 合同标的
1.1 本协议所指保密信息包括：________________________
1.2 保密信息可以书面、口头、电子等形式存在。
1.3 以下信息不属于保密信息：________________________

第二条 价款与支付
2.1 本协议为无偿保密协议，双方不因此产生费用。

第三条 双方权利义务
3.1 乙方承诺对甲方的保密信息严格保密，不得向第三方披露。
3.2 乙方仅可在履行本协议目的范围内使用保密信息。
3.3 本协议有效期为自签署之日起____年。

第四条 违约责任
4.1 乙方违反本协议约定的，应向甲方支付违约金人民币________元。

第五条 保密
5.1 保密义务在本协议期满后继续有效____年。

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

# Labor contract specific field definitions
FIELD_LIST_LABOR = [
    "用人单位", "法定代表人", "用人单位住所",
    "劳动者", "身份证号", "联系电话",
    "合同期限",
    "试用期", "试用期工资",
    "岗位", "工作地点",
    "工时制度",
    "基本工资", "发薪日",
    "社保",
    "竞业限制",
    "劳动仲裁",
]

FIELD_QUESTIONS_LABOR = {
    "用人单位": "请提供用人单位（甲方）的公司全称是什么？",
    "法定代表人": "用人单位的法定代表人是谁？注册地址是哪里？",
    "用人单位住所": "",
    "劳动者": "请提供劳动者（乙方）的姓名是？",
    "身份证号": "劳动者的身份证号码是多少？",
    "联系电话": "劳动者的联系电话是多少？",
    "合同期限": "请问合同期限类型是什么？（固定期限/无固定期限/以完成一定工作任务为期限）",
    "试用期": "试用期是多长时间？",
    "试用期工资": "试用期期间的工资是多少？（不低于正式工资的80%）",
    "岗位": "劳动者的岗位名称是什么？",
    "工作地点": "工作地点在哪里？",
    "工时制度": "采用什么工时制度？（标准工时/综合计算工时/不定时工作制）",
    "基本工资": "月基本工资是多少？每月几号发放工资？",
    "发薪日": "",
    "社保": "是否依法为劳动者缴纳五险（养老、医疗、失业、工伤、生育）？",
    "竞业限制": "是否有竞业限制、服务期或培训违约金约定？",
    "劳动仲裁": "劳动争议管辖的仲裁委员会是哪个？",
}

QUESTION_TO_FIELD_LABOR = {v: k for k, v in FIELD_QUESTIONS_LABOR.items() if v}

SLOT_EXTRACTION_MAP_LABOR = {
    "用人单位": re.compile(r"(?:用人单位|雇主|公司全称|甲方|单位名称)[：:是叫]?\s*([^\n，,。.]+)"),
    "法定代表人": re.compile(r"(?:法定代表人|法人代表|法定代表)[：:是叫]?\s*([^\n，,。.]+)"),
    "用人单位住所": re.compile(r"(?:住所|地址|注册地址|单位地址|办公地址)[：:是叫]?\s*([^\n，,。.]+)"),
    "劳动者": re.compile(r"(?:劳动者|员工|乙方|雇员|姓名)[：:是叫]?\s*([^\n，,。.]+)"),
    "身份证号": re.compile(r"(?:身份证|身份证号|身份证号码)[：:是叫]?\s*([0-9Xx]{15,18})"),
    "联系电话": re.compile(r"(?:联系|电话|手机|手机号)[：:是叫]?\s*([0-9\-（）()]{7,15})"),
    "合同期限": re.compile(r"(?:合同期限|合同类型|期限类型)[：:是叫]?\s*([^\n，,。.]+)"),
    "试用期": re.compile(r"(?:试用期期限|试用期)[：:是叫]?\s*([^\n，,。.]+)"),
    "试用期工资": re.compile(r"(?:试用期)?工资[：:是叫]?\s*([0-9，,.\d]+[万亿元元]*)"),
    "岗位": re.compile(r"(?:岗位|职位|职务|工种)[：:是叫]?\s*([^\n，,。.]+)"),
    "工作地点": re.compile(r"(?:工作地点|工作地|上班地点|办公地点)[：:是叫]?\s*([^\n，,。.]+)"),
    "工时制度": re.compile(r"(?:工时|工时制度|工作时间制度)[：:是叫]?\s*([^\n，,。.]+)"),
    "基本工资": re.compile(r"(?:基本工资|底薪)[：:是叫]?\s*([0-9，,.\d]+[万亿元元]*)"),
    "发薪日": re.compile(r"(?:发薪日|发薪|工资发放日|发放日)[：:是叫]?\s*([^\n，,。.]+)"),
    "社保": re.compile(r"(?:社保|社会保险|五险|五险一金)[：:是叫]?\s*([^\n，,。.]+)"),
    "竞业限制": re.compile(r"(?:竞业|竞业限制|竞业禁止|保密|服务期|培训)[：:是叫]?\s*([^\n，,。.]+)"),
    "劳动仲裁": re.compile(r"(?:仲裁|劳动仲裁|争议|管辖)[：:是叫]?\s*([^\n，,。.]+)"),
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


def _extract_slots_labor(text: str) -> dict:
    slots = {}
    for key, regex in SLOT_EXTRACTION_MAP_LABOR.items():
        match = regex.search(text)
        if match:
            slots[key] = match.group(1).strip()
    return slots


def _all_slots_from_messages_labor(messages: list[dict], from_system: bool = False) -> dict:
    all_slots = {}
    for m in messages:
        if m["role"] == "user":
            all_slots.update(_extract_slots_labor(m.get("content", "")))
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


def _infer_field_from_context_labor(messages: list[dict]) -> str | None:
    for m in reversed(messages[:-1]):
        if m["role"] in ("assistant", "agent"):
            for q_text, field in QUESTION_TO_FIELD_LABOR.items():
                if q_text in m.get("content", ""):
                    return field
            for field in FIELD_LIST_LABOR:
                if f"请问{field}" in m.get("content", ""):
                    return field
            break
    return None


def _mock_chat_labor(messages: list[dict]) -> str:
    last = messages[-1]["content"] if messages else ""

    all_slots = _all_slots_from_messages_labor(messages)
    last_slots = _extract_slots_labor(last)

    if not last_slots:
        inferred = _infer_field_from_context_labor(messages)
        if inferred and inferred not in all_slots:
            all_slots[inferred] = last.strip()
            last_slots[inferred] = last.strip()

    filled_set = set(all_slots.keys())
    missing = [f for f in FIELD_LIST_LABOR if f not in filled_set]

    ack_parts = []
    for k, v in last_slots.items():
        ack_parts.append(f"好的，已记录「{k}：{v}」")
    ack = "，".join(ack_parts) + "。" if ack_parts else ""

    if missing and ack:
        question = FIELD_QUESTIONS_LABOR.get(missing[0], f"请问{missing[0]}是什么？")
        reply = f"{ack} {question}"
    elif missing:
        reply = FIELD_QUESTIONS_LABOR.get(missing[0], f"请问{missing[0]}是什么？")
    elif ack:
        reply = f"{ack} 所有劳动合同信息已收集完成！您可以点击「生成合同」按钮来生成合同初稿。"
    else:
        reply = "所有劳动合同信息已收集完成！您可以点击「生成合同」按钮来生成合同初稿。"

    if all_slots:
        return json.dumps({"content": reply, "slots": all_slots}, ensure_ascii=False)
    return reply


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

    if type_name == "劳动合同":
        return _mock_chat_labor(messages)

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

    labor_replacements = {
        "用人单位": (r"甲方（用人单位）[：:]\s*_{2,}", "甲方（用人单位）：{v}"),
        "法定代表人": (r"法定代表人[：:]\s*_{2,}", "法定代表人：{v}"),
        "用人单位住所": (r"住所地[：:]\s*_{2,}", "住所地：{v}"),
        "劳动者": (r"乙方（劳动者）[：:]\s*_{2,}", "乙方（劳动者）：{v}"),
        "身份证号": (r"身份证号码[：:]\s*_{2,}", "身份证号码：{v}"),
        "联系电话": (r"联系电话[：:]\s*_{2,}", "联系电话：{v}"),
        "合同期限": (r"本合同期限类型为[：:]\s*_{2,}", "本合同期限类型为：{v}"),
        "试用期工资": (r"试用期工资为人民币[：:]\s*_{2,}", "试用期工资为人民币：{v}"),
        "岗位": (r"乙方同意在[：:]\s*_{2,}(?:岗位)", "乙方同意在{v}岗位"),
        "工作地点": (r"工作地点(?:为)?[：:]\s*_{2,}", "工作地点：{v}"),
        "工时制度": (r"甲方实行[：:]\s*_{2,}(?:工时制度)", "甲方实行{v}工时制度"),
        "基本工资": (r"基本工资[：:]\s*_{2,}", "基本工资：{v}"),
        "社保": (r"社会保险自[：:]\s*__", "社会保险自{v}"),
        "竞业限制": (r"竞业限制约定[：:]\s*_{2,}", "竞业限制约定：{v}"),
        "劳动仲裁": (r"可向[：:]\s*_{2,}(?:劳动争议仲裁委员会)", "可向{v}劳动争议仲裁委员会"),
    }

    for key, (pattern, fmt) in labor_replacements.items():
        if key in slots:
            v = slots[key].strip('"').strip()
            text = re.sub(pattern, fmt.format(v=v), text)

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
                if name == "劳动合同":
                    slots = _all_slots_from_messages_labor(messages, from_system=True)
                else:
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
            content_text = data["content"]
            for char in content_text:
                yield char
            return
    except (json.JSONDecodeError, TypeError):
        pass
    for char in text:
        yield char
