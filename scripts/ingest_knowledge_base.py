"""知识库文件 → ChromaDB 向量索引 导入脚本

用法:
    cd legal-secretary
    python scripts/ingest_knowledge_base.py

遍历 knowledge_base/ 下所有模板 JSON 和法律文档 MD，
按预设策略分块 → 生成 embedding → 存入 ChromaDB + SQLite LawArticle 表。

注意：需先在项目根目录运行，或确保 backend/ 在 PYTHONPATH 中。
"""

import json
import os
import re
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# 让 app 包可导入（backend/app/ 是 Python package）
# 方法：把 backend 加入 sys.path，这样 import app.xxx 就能找到 backend/app/
backend_dir = os.path.join(PROJECT_ROOT, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.config import settings
from app.models.base import Base
from app.models.knowledge_base import LawArticle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ── 路径 ──────────────────────────────────────────────────
KB_DIR = os.path.join(PROJECT_ROOT, "knowledge_base")
DB_URL = settings.DATABASE_URL


def get_source_label(file_rel: str) -> str:
    return file_rel.replace("\\", "/")


def chunk_markdown(filepath: str, rel_path: str) -> list[dict]:
    """将 Markdown 文件按 ## 二级标题分块"""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    blocks = re.split(r"\n(?=## )", text)
    chunks = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        heading = ""
        for line in lines:
            if line.startswith("## "):
                heading = line.replace("## ", "").strip()
                break
            if line.startswith("# "):
                heading = line.replace("# ", "").strip()
                break
        if not heading:
            heading = os.path.splitext(os.path.basename(filepath))[0]

        content = "\n".join(lines).strip()
        chunks.append({
            "source": get_source_label(rel_path),
            "content": content,
            "category": "legal_doc",
        })
    return chunks


def chunk_template_json(filepath: str, rel_path: str) -> list[dict]:
    """将合同模板 JSON 文件分块"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    contract_type = data.get("contract_type", "")
    display_name = data.get("display_name", "")
    base_source = get_source_label(rel_path)
    chunks = []

    # clauses[]
    for clause in data.get("clauses", []):
        title = clause.get("title", "")
        content = clause.get("content", "")
        risk_tips = clause.get("risk_tips", "")
        full_content = content
        if risk_tips:
            full_content += f"\n\n【风险提示】{risk_tips}"
        chunks.append({
            "source": base_source,
            "content": full_content,
            "category": f"template_clause|{contract_type}",
        })

    # sections[].content_template
    for section in data.get("sections", []):
        title = section.get("title", "")
        content = section.get("content_template", "")
        if content:
            chunks.append({
                "source": base_source,
                "content": f"【{title}】\n{content}",
                "category": f"template_section|{contract_type}",
            })

    # risk_points[]
    for rp in data.get("risk_points", []):
        rtype = rp.get("risk_type", "")
        desc = rp.get("risk_description", "")
        suggestion = rp.get("suggestion", "")
        full_content = f"【{rtype}】{desc}\n防范建议：{suggestion}"
        chunks.append({
            "source": base_source,
            "content": full_content,
            "category": f"template_risk|{contract_type}",
        })

    return chunks


def ingest_all():
    engine = create_engine(DB_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    # 清空已有 LawArticle 记录
    deleted = db.query(LawArticle).delete()
    db.commit()
    print(f"[OK] Cleared {deleted} old records")

    added = 0
    for root, dirs, files in os.walk(KB_DIR):
        files = [f for f in files if f != ".gitkeep" and not f.startswith(".")]
        for filename in sorted(files):
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, KB_DIR)

            if filename.endswith(".md"):
                chunks = chunk_markdown(filepath, rel_path)
            elif filename.endswith(".json"):
                chunks = chunk_template_json(filepath, rel_path)
            else:
                print(f"  [SKIP] {rel_path}")
                continue

            for chunk in chunks:
                article = LawArticle(
                    title=os.path.splitext(filename)[0],
                    source=chunk["source"],
                    content=chunk["content"],
                    category=chunk["category"],
                )
                db.add(article)
                added += 1

            print(f"  [OK] {rel_path} -> {len(chunks)} chunks")

    db.commit()
    print(f"\n[OK] Total {added} LawArticle records written")

    # ── ChromaDB 同步 ────────────────────────────────────
    try:
        from app.services.rag_engine import RagEngine
        rag = RagEngine(db)
        synced = rag.sync_all()
        print(f"[OK] ChromaDB sync: {synced} entries")
    except Exception as e:
        print(f"[WARN] ChromaDB sync skipped ({e})")
        print("   DB write completed. Run RagEngine.sync_all() manually later.")

    db.close()
    print("[DONE] Knowledge base ingestion complete")


if __name__ == "__main__":
    ingest_all()
