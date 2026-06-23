"""主控Agent：意图识别与任务路由"""


class AgentOrchestrator:
    def __init__(self):
        self.intent_map = {
            "draft": "dialogue_agent",
            "generate": "contract_agent",
            "analyze": "risk_agent",
        }

    def route(self, intent: str, context: dict) -> str:
        agent = self.intent_map.get(intent, "dialogue_agent")
        return agent

    async def process(self, intent: str, context: dict) -> str:
        agent = self.route(intent, context)
        if agent == "dialogue_agent":
            from agent.dialogue_agent import DialogueAgent
            return await DialogueAgent().run(context)
        elif agent == "contract_agent":
            from agent.contract_agent import ContractAgent
            return await ContractAgent().run(context)
        elif agent == "risk_agent":
            from agent.risk_agent import RiskAgent
            return await RiskAgent().run(context)
        return ""
