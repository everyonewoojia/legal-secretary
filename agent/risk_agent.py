"""风险分析Agent：差异分析与风险识别"""


class RiskAgent:
    async def run(self, context: dict) -> str:
        diff_text = context.get("diff_text", "")
        contract_type = context.get("contract_type", "")

        prompt = (
            f"你是法务小秘的风险分析助手。\n"
            f"合同类型：{contract_type}\n"
            f"修改差异：{diff_text}\n"
            f"请分析上述修改中的法律风险，输出JSON数组，"
            f"每个元素包含：clause_title, risk_level(high/medium/low), risk_desc, advice"
        )
        return prompt

    async def generate_reply(self, risk_item: dict) -> str:
        prompt = (
            f"你是一名法务专家，请针对以下风险项生成反驳话术：\n"
            f"条款：{risk_item.get('clause_title')}\n"
            f"风险等级：{risk_item.get('risk_level')}\n"
            f"风险描述：{risk_item.get('risk_desc')}\n"
            f"请提供两套方案：方案一（强硬回绝，附法条支持），方案二（折中妥协）。"
        )
        return prompt
