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
