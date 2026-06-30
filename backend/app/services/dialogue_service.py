import json
from typing import AsyncGenerator

from app.services.ai_service import chat_once, chat_once_json, chat_stream

CONTRACT_TYPE_NAMES = {
    1: "技术服务合同",
    2: "采购合同",
    3: "劳动合同",
    4: "合作协议",
    5: "保密协议",
}

FIELDS_MAP = {
    1: ["甲方信息", "乙方信息", "服务内容", "服务期限", "服务费用", "付款方式", "违约责任", "争议解决"],
    2: ["买方信息", "卖方信息", "商品名称", "数量规格", "单价总价", "交货时间", "付款方式", "验收标准", "违约责任"],
    3: ["用人单位", "劳动者", "岗位职责", "工作地点", "合同期限", "薪酬福利", "工作时间", "解除条件"],
    4: ["甲方信息", "乙方信息", "合作内容", "合作期限", "利益分配", "退出机制", "保密义务"],
    5: ["披露方", "接收方", "保密范围", "保密期限", "违约责任", "例外条款"],
}

SYSTEM_PROMPT_TEMPLATE = """你是法务小秘的 AI 合同助手，专门负责引导用户起草【{contract_type}】。

你需要通过多轮对话收集以下信息：
{fields}

规则：
1. 用自然、友好的语气引导用户，每次可以问 1-2 个问题。
2. 用户可能在一句话中提供多个字段的信息，请一次性全部提取。
3. 用户也可能跳着回答，请灵活归类到对应字段，不要强制按顺序。
4. 已经收集到的字段不要再问，只追问缺失的字段。
5. 所有字段收集完毕后，输出 JSON 格式的总结。
6. 保持专业、友好的语气，使用中文法律文书风格。
7. 重要：当用户说"我是XX公司"时，不要擅自认定他是甲方还是乙方。先问清楚用户代表哪一方，例如"请问您这边是甲方还是乙方？"

输出格式参考：
- 提问时：正常对话文本，如"好的，已记录甲方信息。请问乙方（受托方）的公司全称是什么？"
- 用户已回答但仍有字段缺失时：先确认已收集的信息，再自然追问下一个缺失字段
- 所有字段收集完成时：用自然的语言告诉用户"所有合同信息已收集完成，您可以点击生成合同按钮来生成合同全文"。不要输出 JSON 格式。"""

GENERATION_REQUIREMENTS = {
    1: """## 合同类型：技术服务合同
## 必备条款
1. 合同主体信息（甲方委托方、乙方服务方）
2. 鉴于条款（合作背景与目的）
3. 服务内容与范围（具体技术服务的描述、交付物清单、技术指标）
4. 服务期限与地点
5. 服务费用与支付方式（总金额、付款节点、发票）
6. 双方权利义务（甲方提供条件、乙方交付义务）
7. 验收标准与程序（验收指标、验收期限、验收流程）
8. 培训与技术支持（如有）
9. 知识产权归属（项目成果归属、背景知识产权）
10. 保密条款（保密范围、保密期限）
11. 违约责任（违约金比例、赔偿范围）
12. 争议解决（管辖法院或仲裁）
13. 通知送达、生效与份数""",

    2: """## 合同类型：采购合同
## 必备条款
1. 合同主体信息（甲方买方、乙方卖方）
2. 鉴于条款
3. 采购标的（产品名称、规格型号、数量、质量标准）
4. 合同价款（单价、总价、含税情况）
5. 交付与验收（交付时间、交付地点、验收期限、验收标准）
6. 付款方式（预付款比例、尾款比例、付款条件）
7. 质量保证与质保期（质保期限、保修范围）
8. 包装与运输（包装标准、运输责任、运费承担）
9. 违约责任（逾期交货、逾期付款的违约金）
10. 争议解决
11. 通知送达、生效与份数""",

    3: """## 合同类型：劳动合同
## 必备条款
1. 合同主体（用人单位、劳动者基本信息）
2. 合同期限（固定期限/无固定期限/完成工作任务为期限、试用期）
3. 工作内容与地点（岗位、工作地点）
4. 工作时间与休息休假（标准工时制/综合计算工时制、法定休假）
5. 劳动报酬（月工资、试用期工资、发放日）
6. 社会保险与福利（五险一金）
7. 劳动保护与职业危害防护
8. 合同解除与终止条件
9. 竞业限制与保密（如有）
10. 争议解决（劳动仲裁）""",

    4: """## 合同类型：合作协议
## 必备条款
1. 合作各方主体信息（名称、资质、联系方式）
2. 合作宗旨与合作内容（项目名称、合作模式：联营/渠道分销/资源置换/联合运营/项目合伙等）
3. 各方投入内容（资金、场地、技术、客户资源、人力、品牌授权等）
4. 合作期限与实施地点
5. 项目分工与各方权责清单（明确谁负责运营、招商、财务、风控、交付）
6. 费用承担与收益分配（成本承担方式、营收结算周期、利润分配比例、税费承担）
7. 财务监管规则（对账周期、收支审批、票据管理、保证金约定）
8. 合作退出机制（单方退出条件、解散条件、资产清算、债权债务划分）
9. 知识产权与品牌使用权限（项目成果归属、背景知识产权、品牌授权范围）
10. 禁止同业竞争约定
11. 保密条款（保密范围、保密期限）
12. 不可抗力与违约责任
13. 争议管辖、通知送达、合同生效与份数""",

    5: """## 合同类型：保密协议
## 必备条款
1. 签约双方主体信息
2. 保密信息定义与范围（涉密内容：技术资料、方案、报价、客户数据、财务数据、商业计划、人员信息、未公开技术、合同文件等）
3. 例外情形（公开信息、合法获取信息等不属于保密信息）
4. 保密义务内容（不得泄露、复制、传播、向第三方披露；仅限合作必要范围内使用；采取加密与权限管控等保密措施）
5. 保密期限（协议有效期内 + 协议终止后延续保密年限，核心商业秘密可约定永久保密）
6. 涉密信息使用限制（禁止用于合作外任何目的，禁止擅自许可第三方）
7. 离职/合作终止后返还或销毁涉密载体义务
8. 泄密违约责任（违约金标准、实际损失赔偿范围含律师费等维权成本）
9. 保密义务的独立性（主合同无效保密条款依然有效）
10. 争议解决、通知送达、生效条款""",
}

GENERATION_PROMPT_TEMPLATE = """你是法务小秘的合同生成专家。

请根据以下收集的合同要素，生成一份完整的【{contract_type}】。

## 收集的要素
{fields_json}

## 参考法律依据
{law_context}

## 生成要求
{requirements}

## 通用格式要求
1. 合同格式规范，条款完整，语言严谨。
2. 必须包含：合同主体信息、鉴于条款、正文条款、签署页。
3. 使用中文法律文书标准用语。
4. 生成纯文本格式即可，无需 Markdown 特殊格式。

请直接输出合同全文："""

PLAN_PROMPT_TEMPLATE = """你是法务小秘的合同生成专家。

请根据以下收集的合同要素，先制定一份合同大纲（plan），待用户确认后再生成全文。

## 合同类型
{contract_type}

## 收集的要素
{fields_json}

## 生成要求
{requirements}

## 任务
1. 先输出合同大纲（条款提纲），列出所有将包含的条款标题及每条的简要内容说明。
2. 用语气提示用户确认大纲，例如："以上是合同大纲，请确认是否按照此大纲生成合同全文？如有调整请告知。"
3. 不要直接生成合同全文。

请输出合同大纲："""

RISK_ANALYSIS_PROMPT = """你是一位资深法务专家，正在审查合同修改稿。

## 原始条款
{original}

## 修改后的条款
{modified}

请对比分析以上修改，识别其中对我方不利的风险条款，输出 JSON 数组格式的风险分析结果。
要求：
- 逐条对比原始和修改后的条款，找出每处差异
- 每个差异点生成一条风险项
- 尽量覆盖所有存在风险的条款，不要遗漏
- 风险级别按实际严重程度评估

输出格式：
[
  {{
    "clause_location": "条款位置",
    "risk_type": "风险类型",
    "risk_level": "high/medium/low",
    "description": "风险描述",
    "suggestion": "修改建议",
    "legal_basis": "法律依据"
  }}
]

只输出 JSON 数组，不要其他文字。"""

COUNTER_ARGUMENT_PROMPT = """你是法务小秘的谈判助手，正在为我方业务人员生成谈判话术。

## 风险条款信息
{risk_info}

## 谈判风格：{style}

请生成两套谈判方案，以 JSON 格式输出：
{{
  "plan_a": "【强硬方案】...（附法条支持）",
  "plan_b": "【折中方案】...（双方可接受的妥协条款）"
}}

只输出 JSON，不要其他文字。"""


class DialogueService:
    def __init__(self, contract_type_id: int):
        self.contract_type_id = contract_type_id
        self.type_name = CONTRACT_TYPE_NAMES.get(contract_type_id, "合同")
        self.fields = FIELDS_MAP.get(contract_type_id, [])

    def build_system_prompt(self) -> str:
        fields_str = "\n".join(f"- {f}" for f in self.fields)
        return SYSTEM_PROMPT_TEMPLATE.format(contract_type=self.type_name, fields=fields_str)

    def _get_requirements(self) -> str:
        return GENERATION_REQUIREMENTS.get(self.contract_type_id, "1. 合同格式规范，条款完整，语言严谨。\n2. 使用中文法律文书标准用语。")

    def build_generation_prompt(self, collected_fields: dict, law_context: str = "") -> str:
        law_context = law_context or "（无相关法条引用）"
        return GENERATION_PROMPT_TEMPLATE.format(
            contract_type=self.type_name,
            fields_json=json.dumps(collected_fields, ensure_ascii=False, indent=2),
            law_context=law_context,
            requirements=self._get_requirements(),
        )

    def build_plan_prompt(self, collected_fields: dict) -> str:
        return PLAN_PROMPT_TEMPLATE.format(
            contract_type=self.type_name,
            fields_json=json.dumps(collected_fields, ensure_ascii=False, indent=2),
            requirements=self._get_requirements(),
        )

    async def chat(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        system_prompt = self.build_system_prompt()
        mapped = [
            {"role": "assistant" if m["role"] == "agent" else m["role"], "content": m["content"]}
            for m in messages
        ]
        full_messages = [{"role": "system", "content": system_prompt}, *mapped]
        async for chunk in chat_stream(full_messages):
            yield chunk

    async def extract_fields(self, messages: list[dict]) -> dict | None:
        prompt = f"""你正在引导用户起草【{self.type_name}】。请根据以下对话历史，提取用户已提供的所有合同字段信息，以 JSON 格式输出。

对话历史：
{json.dumps([{"role": m["role"], "content": m["content"][:200]} for m in messages[-6:]], ensure_ascii=False, indent=2)}

只输出 JSON，格式如：{{"字段名": "值", ...}}。如果还没有任何字段，输出 {{}}。"""
        reply = await chat_once([{"role": "system", "content": prompt}])
        try:
            return json.loads(reply)
        except (json.JSONDecodeError, TypeError):
            return None

    async def generate_plan(self, collected_fields: dict) -> str:
        return await chat_once([
            {"role": "system", "content": self.build_plan_prompt(collected_fields)},
        ])

    async def generate_contract(self, collected_fields: dict, law_context: str = "") -> str:
        return await chat_once([
            {"role": "system", "content": self.build_generation_prompt(collected_fields, law_context)},
        ])

    async def generate_contract_stream(self, collected_fields: dict, law_context: str = "") -> AsyncGenerator[str, None]:
        prompt = self.build_generation_prompt(collected_fields, law_context)
        async for chunk in chat_stream([{"role": "system", "content": prompt}], temperature=0.0):
            yield chunk


async def analyze_risks(original: str, modified: str, law_context: str = "") -> list[dict]:
    prompt = RISK_ANALYSIS_PROMPT.format(original=original, modified=modified)
    if law_context:
        prompt += f"\n\n## 参考法律依据\n{law_context}"
    result = await chat_once_json([
        {"role": "system", "content": prompt},
    ])
    if isinstance(result, list):
        return result
    return []


async def generate_counter_argument(risk_info: dict, style: str = "balanced") -> dict:
    result = await chat_once_json([
        {"role": "system", "content": COUNTER_ARGUMENT_PROMPT.format(
            risk_info=json.dumps(risk_info, ensure_ascii=False),
            style=style,
        )},
    ])
    return result
