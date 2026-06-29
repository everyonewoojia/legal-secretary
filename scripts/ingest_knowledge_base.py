"""知识库文件 → ChromaDB 向量索引 导入脚本

用法:
    cd legal-secretary
    PYTHONPATH=backend python scripts/ingest_knowledge_base.py

遍历 knowledge_base/ 下所有模板 JSON 和法律文档 MD，
按预设策略分块 → 生成 embedding → 存入 ChromaDB + SQLite LawArticle 表。

注意：需确保 backend/ 在 PYTHONPATH 中，或启动命令使用 PYTHONPATH=backend。
"""

import json
import os
import re
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# 把 backend 加入 sys.path，使 import app.xxx 能找到 backend/app/
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

# 已知的清单/元数据文件，不应作为知识源导入
SKIP_FILES = {"index.json", "index_metadata.json", "faiss_index.bin", ".gitkeep"}
SKIP_DIRS = {"__pycache__"}
# 底线规则文件名，有专用提取逻辑
BOTTOM_LINE_FILE = "bottom_line_rules.json"


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


def _extract_item_chunks(item: dict, base_source: str) -> list[dict]:
    """从单个 dict item 中提取 clauses/sections/risk_points 生成 chunk"""
    contract_type = item.get("contract_type", "")
    display_name = item.get("display_name", "")
    chunks = []

    # clauses[]
    for clause in item.get("clauses", []):
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
    for section in item.get("sections", []):
        title = section.get("title", "")
        content = section.get("content_template", "")
        if content:
            chunks.append({
                "source": base_source,
                "content": f"【{title}】\n{content}",
                "category": f"template_section|{contract_type}",
            })

    # risk_points[]
    for rp in item.get("risk_points", []):
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


def chunk_template_json(filepath: str, rel_path: str) -> list[dict]:
    """将合同模板 JSON 文件分块

    兼容顶层为 dict 或 list：
    - dict  → 按原逻辑提取 contract_type/display_name/clauses/sections/risk_points
    - list  → 遍历每个 item，尝试按 dict 提取
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    base_source = get_source_label(rel_path)
    chunks = []

    if isinstance(data, dict):
        chunks.extend(_extract_item_chunks(data, base_source))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                chunks.extend(_extract_item_chunks(item, base_source))
            else:
                print(f"  [WARN] {rel_path}[{i}] 不是 dict，已跳过")
    else:
        print(f"  [WARN] {rel_path} 顶层不是 dict 也不是 list，已跳过")

    return chunks


def chunk_bottom_line_rules(filepath: str, rel_path: str) -> list[dict]:
    """从 bottom_line_rules.json 提取每条规则为 chunk"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 兼容顶层是 dict（含 rules/meta）或直接是 list
    if isinstance(data, dict):
        rules = data.get("rules", data.get("items", []))
    elif isinstance(data, list):
        rules = data
    else:
        print(f"  [WARN] {rel_path} 结构无法识别，已跳过")
        return []

    base_source = get_source_label(rel_path)
    chunks = []
    for i, rule in enumerate(rules):
        if not isinstance(rule, dict):
            print(f"  [WARN] {rel_path} 规则[{i}] 不是 dict，已跳过")
            continue

        name = rule.get("name", "")
        description = rule.get("description", "")
        risk_level = rule.get("risk_level", "")
        trigger_keywords = rule.get("trigger_keywords", [])
        bottom_line = rule.get("bottom_line", "")
        recommended_response = rule.get("recommended_response", "")
        negotiation_strategy = rule.get("negotiation_strategy", {})

        # 将关键信息拼成文本块
        kw_text = "、".join(trigger_keywords) if isinstance(trigger_keywords, list) else str(trigger_keywords)
        content = f"【规则】{name}（风险等级：{risk_level}）\n"
        content += f"{description}\n"
        if kw_text:
            content += f"触发关键词：{kw_text}\n"
        content += f"底线：{bottom_line}\n"
        content += f"推荐策略：{recommended_response}\n"

        if isinstance(negotiation_strategy, dict):
            for pos_key in ("firm_position", "compromise_position", "fallback_position"):
                pos = negotiation_strategy.get(pos_key, {})
                if isinstance(pos, dict) and pos.get("script"):
                    content += f"【{pos.get('title', pos_key)}】{pos['script']}\n"

        chunks.append({
            "source": base_source,
            "content": content,
            "category": f"bottom_line_rule|{risk_level}",
        })

    return chunks


def collect_all_chunks() -> list[tuple[str, str, str]]:
    """收集所有知识库文件的 chunk，返回 [(source, content, category), ...]

    仅做文件读取和分块，不涉及数据库操作。
    如果 chunk 总数为 0，调用方应终止流程。
    """
    all_chunks = []

    for root, dirs, files in os.walk(KB_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        files = [f for f in files if not f.startswith(".") and f not in SKIP_FILES]
        for filename in sorted(files):
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, KB_DIR)

            if filename.endswith(".md"):
                chunks = chunk_markdown(filepath, rel_path)
            elif filename.endswith(".json"):
                # 判断是否为底线规则文件
                if filename == BOTTOM_LINE_FILE:
                    chunks = chunk_bottom_line_rules(filepath, rel_path)
                else:
                    chunks = chunk_template_json(filepath, rel_path)
            else:
                print(f"  [SKIP] {rel_path}")
                continue

            # 过滤掉空 chunk
            valid_chunks = [c for c in chunks if c.get("content", "").strip()]
            for c in valid_chunks:
                all_chunks.append((c["source"], c["content"], c["category"]))
            if valid_chunks:
                print(f"  [OK] {rel_path} -> {len(valid_chunks)} chunks")
            else:
                print(f"  [INFO] {rel_path} -> 无有效内容，已跳过")

    return all_chunks


def ingest_all():
    print("[INFO] Collecting chunks from knowledge_base/ ...")
    all_chunks = collect_all_chunks()

    if not all_chunks:
        print("[ERROR] 未收集到任何知识块，终止导入（数据库未被修改）")
        sys.exit(1)

    print(f"\n[INFO] 共收集 {len(all_chunks)} 个知识块，开始写入数据库 ...")

    engine = create_engine(DB_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # 清空已有 LawArticle 记录（chunks 已成功收集后才清空）
        deleted = db.query(LawArticle).delete()
        db.commit()
        print(f"[OK] 已清空 {deleted} 条旧记录")

        added = 0
        for source, content, category in all_chunks:
            title = os.path.basename(source)
            article = LawArticle(
                title=title,
                source=source,
                content=content,
                category=category,
            )
            db.add(article)
            added += 1

        db.commit()
        print(f"[OK] 写入 {added} 条 LawArticle 记录")

        # ── ChromaDB 同步 ────────────────────────────────────
        try:
            from app.services.rag_engine import RagEngine
            rag = RagEngine(db)
            synced = rag.sync_all()
            print(f"[OK] ChromaDB 同步: {synced} 条")
        except Exception as e:
            print(f"[WARN] ChromaDB 同步跳过 ({e})")
            print("   DB 写入已完成。可稍后手动运行 RagEngine.sync_all()。")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] 数据库写入失败，已回滚: {e}")
        raise
    finally:
        db.close()

    print("[DONE] 知识库导入完成")


if __name__ == "__main__":
    ingest_all()
