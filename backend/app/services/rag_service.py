from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.knowledge_base import LawArticle
from app.models.template import ContractTemplate
from app.schemas.rag import LawArticleUpdate, TemplateUpdate
from app.services.rag_engine import RagEngine


class RagService:
    def __init__(self, db: Session):
        self.db = db
        self.engine = RagEngine(db)

    def search_law(self, query: str, category: str | None = None, page: int = 1, page_size: int = 20):
        q = self.db.query(LawArticle)
        if query:
            q = q.filter(LawArticle.content.ilike(f"%{query}%"))
        if category:
            q = q.filter(LawArticle.category == category)
        total = q.count()
        items = q.order_by(LawArticle.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def vector_search(self, query: str, top_k: int = 3) -> list[dict]:
        return self.engine.search(query, top_k)

    def get_law_article(self, law_id: int) -> LawArticle | None:
        return self.db.query(LawArticle).filter(LawArticle.id == law_id).first()

    def add_law_article(self, title: str, source: str, content: str, category: str = "") -> LawArticle:
        article = LawArticle(title=title, source=source, content=content, category=category)
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        self.engine.add_document(article)
        return article

    def update_law_article(self, law_id: int, req: LawArticleUpdate) -> LawArticle | None:
        article = self.db.query(LawArticle).filter(LawArticle.id == law_id).first()
        if not article:
            return None
        update_data = req.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(article, field, value)
        self.db.commit()
        self.db.refresh(article)
        self.engine.delete_document(law_id)
        self.engine.add_document(article)
        return article

    def delete_law_article(self, law_id: int) -> bool:
        article = self.db.query(LawArticle).filter(LawArticle.id == law_id).first()
        if not article:
            return False
        self.db.delete(article)
        self.db.commit()
        self.engine.delete_document(law_id)
        return True

    def sync_vector_db(self) -> int:
        return self.engine.sync_all()

    def get_templates(self, type_id: int | None = None) -> list[ContractTemplate]:
        q = self.db.query(ContractTemplate).filter(ContractTemplate.is_active.is_(True))
        if type_id is not None:
            q = q.filter(ContractTemplate.type_id == type_id)
        return q.all()

    def get_template_by_id(self, template_id: int) -> ContractTemplate | None:
        return self.db.query(ContractTemplate).filter(ContractTemplate.id == template_id).first()

    def add_template(self, name: str, type_id: int, description: str, structure: str) -> ContractTemplate:
        tmpl = ContractTemplate(name=name, type_id=type_id, description=description, structure=structure)
        self.db.add(tmpl)
        self.db.commit()
        self.db.refresh(tmpl)
        return tmpl

    def update_template(self, template_id: int, req: TemplateUpdate) -> ContractTemplate | None:
        tmpl = self.db.query(ContractTemplate).filter(ContractTemplate.id == template_id).first()
        if not tmpl:
            return None
        update_data = req.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tmpl, field, value)
        self.db.commit()
        self.db.refresh(tmpl)
        return tmpl

    def delete_template(self, template_id: int) -> bool:
        tmpl = self.db.query(ContractTemplate).filter(ContractTemplate.id == template_id).first()
        if not tmpl:
            return False
        self.db.delete(tmpl)
        self.db.commit()
        return True

    def search_all(self, query: str, contract_type: str = "", top_k: int = 5) -> list[dict]:
        """统一的 RAG 搜索入口：向量检索 + keyword fallback + 知识库文件 fallback"""
        results = self.vector_search(query, top_k)
        if results:
            return results

        # ChromaDB fallback: keyword on LawArticle
        category_filter = f"|{contract_type}" if contract_type else None
        q = self.db.query(LawArticle).filter(LawArticle.content.ilike(f"%{query}%"))
        if category_filter:
            q = q.filter(LawArticle.category.ilike(f"%{category_filter}"))
        articles = q.limit(top_k).all()
        if articles:
            return [
                {
                    "source": a.source,
                    "content": a.content[:500],
                    "score": 0.5,
                    "metadata": {"category": a.category},
                }
                for a in articles
            ]

        # Final fallback: search knowledge_base files on disk
        return self._kb_file_search(query, contract_type, top_k)

    def _kb_file_search(self, query: str, contract_type: str, top_k: int) -> list[dict]:
        """直接在 knowledge_base 磁盘文件中对 clauses[].content 做关键词匹配"""
        import glob as g, json as j, os

        kb_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "knowledge_base")
        results = []

        # 模板文件
        tmpl_pattern = os.path.join(kb_dir, "templates", "*.json")
        for fp in g.glob(tmpl_pattern):
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
                        "metadata": {
                            "clause_title": clause.get("title", ""),
                            "contract_type": ct,
                        },
                    })
                    if len(results) >= top_k:
                        return results

            for section in data.get("sections", []):
                content = section.get("content_template", "")
                if query.lower() in content.lower():
                    results.append({
                        "source": f"templates/{os.path.basename(fp)}",
                        "content": f"【{section.get('title', '')}】\n{content[:500]}",
                        "score": 0.5,
                        "metadata": {
                            "section_title": section.get("title", ""),
                            "contract_type": ct,
                        },
                    })
                    if len(results) >= top_k:
                        return results

        # 法律文档
        doc_pattern = os.path.join(kb_dir, "legal_docs", "*.md")
        for fp in g.glob(doc_pattern):
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    text = f.read()
            except IOError:
                continue
            import re
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
