import os

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.knowledge_base import LawArticle

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings

    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False


class RagEngine:
    def __init__(self, db: Session):
        self.db = db
        self._collection = None
        if HAS_CHROMA:
            try:
                os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
                self._chroma = chromadb.PersistentClient(
                    path=settings.VECTOR_DB_PATH,
                    settings=ChromaSettings(anonymized_telemetry=False),
                )
                self._collection = self._chroma.get_or_create_collection("law_articles")
            except Exception:
                self._collection = None

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if self._collection:
            return self._vector_search(query, top_k)
        return self._keyword_search(query, top_k)

    def _vector_search(self, query: str, top_k: int = 3) -> list[dict]:
        try:
            results = self._collection.query(query_texts=[query], n_results=top_k)
            items = []
            if results["metadatas"]:
                for meta in results["metadatas"][0]:
                    items.append({
                        "id": meta.get("id", 0),
                        "title": meta.get("title", ""),
                        "source": meta.get("source", ""),
                        "content": meta.get("content", ""),
                        "category": meta.get("category", ""),
                        "score": meta.get("score", 0),
                    })
            return items
        except Exception:
            return self._keyword_search(query, top_k)

    def _keyword_search(self, query: str, top_k: int = 3) -> list[dict]:
        articles = (
            self.db.query(LawArticle)
            .filter(LawArticle.content.ilike(f"%{query}%"))
            .limit(top_k)
            .all()
        )
        return [
            {"id": a.id, "title": a.title, "source": a.source, "content": a.content[:500], "category": a.category, "score": 0}
            for a in articles
        ]

    def add_document(self, article: LawArticle) -> bool:
        if not self._collection:
            return False
        try:
            self._collection.add(
                documents=[article.content],
                metadatas=[{
                    "id": article.id,
                    "title": article.title,
                    "source": article.source,
                    "content": article.content[:500],
                    "category": article.category,
                }],
                ids=[f"law_{article.id}"],
            )
            return True
        except Exception:
            return False

    def sync_all(self) -> int:
        if not self._collection:
            return 0
        articles = self.db.query(LawArticle).all()
        count = 0
        for a in articles:
            if self.add_document(a):
                count += 1
        return count

    def delete_document(self, article_id: int) -> bool:
        if not self._collection:
            return False
        try:
            self._collection.delete(ids=[f"law_{article_id}"])
            return True
        except Exception:
            return False
