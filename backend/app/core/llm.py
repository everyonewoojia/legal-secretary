"""LLM 调用入口 — 代理 ai_service 的桥接模块

Agent 层（agent/ 目录）通过此模块调用大模型，
而非直接依赖 services/ai_service，避免循环依赖。
"""

from typing import AsyncGenerator

from app.services.ai_service import chat_once as llm_complete
from app.services.ai_service import chat_once_json as llm_complete_json
from app.services.ai_service import chat_stream as llm_stream

__all__ = ["llm_complete", "llm_complete_json", "llm_stream"]
