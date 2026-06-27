"""Prompt 加载工具"""

import os


_PROMPT_CACHE: dict[str, str] = {}
_PROMPT_DIR = os.path.join(os.path.dirname(__file__))


def load_prompt(name: str) -> str:
    if name in _PROMPT_CACHE:
        return _PROMPT_CACHE[name]

    path = os.path.join(_PROMPT_DIR, f"{name}.txt")
    if not os.path.exists(path):
        # Return default prompt if file not found
        defaults = {
            "dialogue_system": "你是一个法务合同对话助手，负责引导用户补充合同要素。",
            "contract_generation": "你是一个专业的合同生成助手，根据用户提供的要素生成合同。",
            "risk_analysis": "你是一个法务风险分析助手，负责识别合同修改中的法律风险。",
        }
        _PROMPT_CACHE[name] = defaults.get(name, "")
        return _PROMPT_CACHE[name]

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    _PROMPT_CACHE[name] = content
    return content


def reload_prompts():
    _PROMPT_CACHE.clear()
