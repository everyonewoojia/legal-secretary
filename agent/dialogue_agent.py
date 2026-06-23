"""多轮对话引导Agent：槽位抽取与问题生成"""


class DialogueAgent:
    async def run(self, context: dict) -> str:
        message = context.get("message", "")
        contract_type = context.get("contract_type", "")
        slots = context.get("slots", {})

        prompt = (
            f"你是法务小秘的对话引导助手。\n"
            f"当前合同类型：{contract_type}\n"
            f"已收集信息：{slots}\n"
            f"用户消息：{message}\n"
            f"请从用户消息中抽取合同要素，并判断是否需要继续提问。"
            f"如需提问，请输出一个自然的问题；如信息已完整，请回复'[COMPLETE]'。"
        )
        return prompt
