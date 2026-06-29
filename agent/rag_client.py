"""Agent 层 RAG 检索客户端

各 Agent 通过此类查询法律知识库，获取与当前合同/风险相关的法律条文、
模板条款和风险规则。内部调用 RagService.search_all()。
"""

from typing import Any


class RagClient:
    def __init__(self, db_session=None):
        self._db = db_session

    def search(self, query: str, contract_type: str = "", top_k: int = 5) -> list[dict]:
        """语义搜索知识库，返回相关片段列表"""
        if self._db is None:
            return self._direct_file_search(query, contract_type, top_k)
        from app.services.rag_service import RagService
        svc = RagService(self._db)
        return svc.search_all(query, contract_type, top_k)

    def search_legal_basis(self, risk_type: str, contract_type: str = "") -> str:
        """搜索与指定风险类型相关的法律依据文本"""
        results = self.search(f"{risk_type} 法律依据 法律规定", contract_type, top_k=3)
        if not results:
            return ""
        texts = []
        for r in results:
            content = r.get("content", "")
            if len(content) > 60:
                texts.append(content)
        return "\n\n".join(texts[:3])

    def search_clause_template(self, clause_title: str, contract_type: str) -> str:
        """搜索指定条款的模板内容"""
        results = self.search(f"{clause_title} {contract_type}", contract_type, top_k=2)
        for r in results:
            meta = r.get("metadata", {})
            if meta.get("clause_title") == clause_title or meta.get("section_title") == clause_title:
                return r.get("content", "")
        return ""

    def search_risk_rules(self, contract_type: str = "") -> str:
        """搜索风险审查规则"""
        results = self.search("谈判风险审查规则 风险", contract_type, top_k=5)
        texts = [r.get("content", "") for r in results if r.get("content")]
        return "\n\n".join(texts[:3])

    def _direct_file_search(self, query: str, contract_type: str, top_k: int) -> list[dict]:
        """无 DB 连接时的文件直搜 fallback"""
        import glob as g, json as j, os, re

        kb_dir = self._find_kb_dir()
        if not kb_dir:
            return []
        results = []
        for fp in g.glob(os.path.join(kb_dir, "templates", "*.json")):
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    data = j.load(f)
            except (j.JSONDecodeError, IOError):
                continue
            ct = data.get("contract_type", "")
            if contract_type and ct != contract_type:
                continue
            for clause in data.get("clauses", []):
                content = clause.get("content", "")
                if query.lower() in content.lower():
                    results.append({
                        "source": f"templates/{os.path.basename(fp)}",
                        "content": content[:500],
                        "score": 0.6,
                        "metadata": {"clause_title": clause.get("title", ""), "contract_type": ct},
                    })
                    if len(results) >= top_k:
                        return results
        for fp in g.glob(os.path.join(kb_dir, "legal_docs", "*.md")):
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    text = f.read()
            except IOError:
                continue
            blocks = re.split(r"\n(?=## )", text)
            for block in blocks:
                if query.lower() in block.lower():
                    results.append({
                        "source": f"legal_docs/{os.path.basename(fp)}",
                        "content": block[:500],
                        "score": 0.4,
                        "metadata": {"type": "legal_doc"},
                    })
                    if len(results) >= top_k:
                        return results
        return results

    @staticmethod
    def _find_kb_dir() -> str | None:
        import os
        for candidate in [
            os.path.join(os.path.dirname(__file__), "..", "knowledge_base"),
            os.path.join(os.getcwd(), "knowledge_base"),
        ]:
            norm = os.path.normpath(candidate)
            if os.path.isdir(norm):
                return norm
        return None
