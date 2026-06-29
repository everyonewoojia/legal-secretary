from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.common import Response
from app.schemas.rag import (
    LawArticleCreate,
    LawArticleResponse,
    LawArticleUpdate,
    RagSearchRequest,
    RagSearchResult,
    TemplateCreate,
    TemplateResponse,
    TemplateUpdate,
)
from app.services.rag_service import RagService

router = APIRouter()


@router.post("/search", response_model=Response)
def rag_search(req: RagSearchRequest, db: Session = Depends(get_db)):
    svc = RagService(db)
    results = svc.search_all(req.query, req.contract_type, req.top_k)
    return Response(data={
        "query": req.query,
        "total": len(results),
        "chunks": [
            RagSearchResult(
                source=r["source"],
                content=r["content"],
                score=r.get("score", 0),
                metadata=r.get("metadata", {}),
            )
            for r in results
        ],
    })


@router.post("/laws", response_model=Response)
def add_law(req: LawArticleCreate, db: Session = Depends(get_db)):
    svc = RagService(db)
    article = svc.add_law_article(req.title, req.source, req.content, req.category)
    return Response(data=LawArticleResponse.model_validate(article))


@router.get("/laws", response_model=Response)
def search_law(
    q: str = "",
    category: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    svc = RagService(db)
    results, total = svc.search_law(q, category, page, page_size)
    return Response(data={"items": [LawArticleResponse.model_validate(r) for r in results], "total": total})


@router.get("/laws/{law_id}", response_model=Response)
def get_law(law_id: int, db: Session = Depends(get_db)):
    svc = RagService(db)
    article = svc.get_law_article(law_id)
    if not article:
        return Response(code=404, message="法条不存在")
    return Response(data=LawArticleResponse.model_validate(article))


@router.put("/laws/{law_id}", response_model=Response)
def update_law(law_id: int, req: LawArticleUpdate, db: Session = Depends(get_db)):
    svc = RagService(db)
    article = svc.update_law_article(law_id, req)
    if not article:
        return Response(code=404, message="法条不存在")
    return Response(data=LawArticleResponse.model_validate(article))


@router.delete("/laws/{law_id}", response_model=Response)
def delete_law(law_id: int, db: Session = Depends(get_db)):
    svc = RagService(db)
    ok = svc.delete_law_article(law_id)
    if not ok:
        return Response(code=404, message="法条不存在")
    return Response()


@router.post("/templates", response_model=Response)
def add_template(req: TemplateCreate, db: Session = Depends(get_db)):
    svc = RagService(db)
    tmpl = svc.add_template(req.name, req.type_id, req.description, req.structure)
    return Response(data=TemplateResponse.model_validate(tmpl))


@router.get("/templates", response_model=Response)
def list_templates(type_id: int | None = None, db: Session = Depends(get_db)):
    svc = RagService(db)
    templates = svc.get_templates(type_id)
    return Response(data=[TemplateResponse.model_validate(t) for t in templates])


@router.get("/templates/{template_id}", response_model=Response)
def get_template(template_id: int, db: Session = Depends(get_db)):
    svc = RagService(db)
    tmpl = svc.get_template_by_id(template_id)
    if not tmpl:
        return Response(code=404, message="模板不存在")
    return Response(data=TemplateResponse.model_validate(tmpl))


@router.put("/templates/{template_id}", response_model=Response)
def update_template(template_id: int, req: TemplateUpdate, db: Session = Depends(get_db)):
    svc = RagService(db)
    tmpl = svc.update_template(template_id, req)
    if not tmpl:
        return Response(code=404, message="模板不存在")
    return Response(data=TemplateResponse.model_validate(tmpl))


@router.delete("/templates/{template_id}", response_model=Response)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    svc = RagService(db)
    ok = svc.delete_template(template_id)
    if not ok:
        return Response(code=404, message="模板不存在")
    return Response()
