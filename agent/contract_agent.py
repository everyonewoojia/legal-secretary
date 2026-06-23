"""合同初稿生成Agent"""


class ContractAgent:
    async def run(self, context: dict) -> str:
        slots = context.get("slots", {})
        contract_type = context.get("contract_type", "")
        rag_context = context.get("rag_context", "")

        prompt = (
            f"你是法务小秘的合同生成助手。\n"
            f"合同类型：{contract_type}\n"
            f"合同要素：{slots}\n"
            f"参考法规：{rag_context}\n"
            f"请根据以上信息生成一份完整的、格式规范的合同初稿。\n"
            f"要求：包含合同编号、双方信息、条款编号、签署日期。"
        )
        return prompt
