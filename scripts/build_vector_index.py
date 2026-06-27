"""
构建 FAISS 向量索引 — 遍历 knowledge_base/ 下所有知识源文件，生成 embedding 并构建索引。

输出:
  - knowledge_base/faiss_index.bin     FAISS 向量索引
  - knowledge_base/index_metadata.json  索引元信息（每个 chunk 对应的来源、类型、标题等）

用法:
  python3 scripts/build_vector_index.py

依赖:
  pip install sentence-transformers faiss-cpu
"""

import json
import os
import re
import sys

# ── 路径配置 ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(BASE_DIR, "knowledge_base")
TEMPLATES_DIR = os.path.join(KB_DIR, "templates")
LEGAL_DOCS_DIR = os.path.join(KB_DIR, "legal_docs")
CLAUSES_FILE = os.path.join(KB_DIR, "clauses", "bottom_line_rules.json")

OUTPUT_INDEX = os.path.join(KB_DIR, "faiss_index.bin")
OUTPUT_METADATA = os.path.join(KB_DIR, "index_metadata.json")

# ── 模型配置 ──────────────────────────────────────────────
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384

# ── 分块提取函数 ──────────────────────────────────────────

def extract_template_chunks(filepath):
    """从合同模板 JSON 中提取 clauses、risk_points、generation_notes 作为文本块"""
    rel_path = os.path.relpath(filepath, BASE_DIR)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks = []
    display_name = data.get("display_name", "")

    # clauses
    for clause in data.get("clauses", []):
        title = clause.get("title", "")
        content = clause.get("content", "")
        risk_tips = clause.get("risk_tips", "")
        text = f"[{display_name}] {title}\n{content}"
        if risk_tips:
            text += f"\n风险提示：{risk_tips}"
        chunks.append({
            "text": text,
            "source_file": rel_path,
            "chunk_type": "template_clause",
            "title": f"{display_name} - {title}",
        })

    # risk_points
    for rp in data.get("risk_points", []):
        text = (
            f"[{display_name}] 风险类型：{rp.get('risk_type', '')}\n"
            f"风险描述：{rp.get('risk_description', '')}\n"
            f"防范建议：{rp.get('suggestion', '')}"
        )
        chunks.append({
            "text": text,
            "source_file": rel_path,
            "chunk_type": "template_risk_point",
            "title": f"{display_name} - {rp.get('risk_type', '风险点')}",
        })

    # generation_notes
    gen_notes = data.get("generation_notes", "")
    if gen_notes:
        chunks.append({
            "text": f"[{display_name}] 生成注意事项\n{gen_notes}",
            "source_file": rel_path,
            "chunk_type": "template_generation_note",
            "title": f"{display_name} - 生成注意事项",
        })

    return chunks


def extract_bottom_line_chunks(filepath):
    """从 bottom_line_rules.json 中提取每条规则为文本块"""
    rel_path = os.path.relpath(filepath, BASE_DIR)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks = []
    for rule in data.get("rules", []):
        name = rule.get("name", "")
        description = rule.get("description", "")
        risk_level = rule.get("risk_level", "")
        review_points = "\n".join(f"- {p}" for p in rule.get("review_points", []))
        bottom_line = rule.get("bottom_line", "")
        firm = rule.get("negotiation_strategy", {}).get("firm_position", {}).get("script", "")
        compromise = rule.get("negotiation_strategy", {}).get("compromise_position", {}).get("script", "")
        fallback = rule.get("negotiation_strategy", {}).get("fallback_position", {}).get("script", "")

        text = (
            f"规则：{name}（风险等级：{risk_level}）\n"
            f"风险描述：{description}\n"
            f"审查要点：\n{review_points}\n"
            f"底线：{bottom_line}\n"
            f"强硬话术：{firm}\n"
            f"折中话术：{compromise}\n"
            f"底线话术：{fallback}"
        )
        chunks.append({
            "text": text,
            "source_file": rel_path,
            "chunk_type": "bottom_line_rule",
            "title": f"底线规则 - {name}",
        })

    return chunks


def extract_markdown_chunks(filepath):
    """将 Markdown 知识库文件按二级标题（##）切分为文本块"""
    rel_path = os.path.relpath(filepath, BASE_DIR)
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = []
    # 按 ## 标题分割
    sections = re.split(r"\n(?=##\s)", text)
    for section in sections:
        section = section.strip()
        if len(section) < 80:
            continue
        lines = section.split("\n")
        title_line = lines[0].lstrip("#").strip() if lines else ""
        # 取前 80 字作为简洁标题
        short_title = title_line[:80] if title_line else "(无标题)"
        chunks.append({
            "text": section,
            "source_file": rel_path,
            "chunk_type": "legal_doc_section",
            "title": short_title,
        })

    return chunks


# ── 主流程 ──────────────────────────────────────────────

def main():
    # 检查依赖
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("错误: 需要安装 sentence-transformers。请运行: pip install sentence-transformers")
        sys.exit(1)

    try:
        import faiss
        import numpy as np
    except ImportError:
        print("错误: 需要安装 faiss-cpu。请运行: pip install faiss-cpu")
        sys.exit(1)

    # 收集所有文本块
    all_chunks = []

    # 1) 合同模板
    if os.path.isdir(TEMPLATES_DIR):
        for fname in sorted(os.listdir(TEMPLATES_DIR)):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(TEMPLATES_DIR, fname)
            try:
                chunks = extract_template_chunks(fpath)
                all_chunks.extend(chunks)
                print(f"  ✅ 模板 {fname}: {len(chunks)} 块")
            except Exception as e:
                print(f"  ⚠️  跳过 {fname}: {e}")

    # 2) 底线规则
    if os.path.isfile(CLAUSES_FILE):
        try:
            chunks = extract_bottom_line_chunks(CLAUSES_FILE)
            all_chunks.extend(chunks)
            print(f"  ✅ 底线规则: {len(chunks)} 块")
        except Exception as e:
            print(f"  ⚠️  读取底线规则失败: {e}")

    # 3) 法律知识库 Markdown
    if os.path.isdir(LEGAL_DOCS_DIR):
        for fname in sorted(os.listdir(LEGAL_DOCS_DIR)):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(LEGAL_DOCS_DIR, fname)
            try:
                chunks = extract_markdown_chunks(fpath)
                all_chunks.extend(chunks)
                print(f"  ✅ 法律文档 {fname}: {len(chunks)} 块")
            except Exception as e:
                print(f"  ⚠️  跳过 {fname}: {e}")

    if not all_chunks:
        print("错误: 未找到任何知识块，请确认 knowledge_base/ 目录下存在有效文件。")
        sys.exit(1)

    print(f"\n共提取 {len(all_chunks)} 个知识块，开始生成 embedding ...")

    # 加载模型并生成 embedding
    model = SentenceTransformer(EMBEDDING_MODEL)
    texts = [c["text"] for c in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    dim = embeddings.shape[1]
    print(f"Embedding 维度: {dim}，共 {len(embeddings)} 个向量")

    # 构建 FAISS 索引
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype(np.float32))

    # 保存
    faiss.write_index(index, OUTPUT_INDEX)

    # 保存元信息（去掉 text 全文，仅保留预览用于展示）
    metadata = []
    for i, chunk in enumerate(all_chunks):
        preview = chunk["text"][:200].replace("\n", " ") + ("..." if len(chunk["text"]) > 200 else "")
        metadata.append({
            "id": i,
            "source_file": chunk["source_file"],
            "chunk_type": chunk["chunk_type"],
            "title": chunk["title"],
            "text_preview": preview,
        })

    with open(OUTPUT_METADATA, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 构建完成！")
    print(f"   索引文件: {OUTPUT_INDEX}")
    print(f"   元信息:   {OUTPUT_METADATA}")
    print(f"   知识块数: {len(all_chunks)}")
    print(f"   向量维度: {dim}")


if __name__ == "__main__":
    main()
