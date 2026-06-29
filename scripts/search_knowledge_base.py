"""
搜索 FAISS 向量索引 — 输入查询文本，返回 Top 5 最相似知识块。

用法:
  python3 scripts/search_knowledge_base.py "违约金过高怎么办"

输出字段:
  score        余弦相似度（0~1）
  source_file  来源文件路径
  chunk_type   块类型（template_clause / template_risk_point / bottom_line_rule / legal_doc_section）
  title        块标题
  text_preview 内容预览（前 200 字）

依赖:
  pip install sentence-transformers faiss-cpu
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(BASE_DIR, "knowledge_base")
INDEX_FILE = os.path.join(KB_DIR, "faiss_index.bin")
METADATA_FILE = os.path.join(KB_DIR, "index_metadata.json")
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 5


def main():
    if len(sys.argv) < 2:
        print("用法: python3 scripts/search_knowledge_base.py <查询文本>")
        print("示例: python3 scripts/search_knowledge_base.py \"违约金过高怎么办\"")
        sys.exit(1)

    query = sys.argv[1].strip()

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

    # 检查索引文件
    if not os.path.isfile(INDEX_FILE):
        print(f"错误: 索引文件不存在: {INDEX_FILE}")
        print("请先运行 python3 scripts/build_vector_index.py 构建索引。")
        sys.exit(1)

    if not os.path.isfile(METADATA_FILE):
        print(f"错误: 元信息文件不存在: {METADATA_FILE}")
        sys.exit(1)

    # 加载
    print(f"正在加载索引 ...")
    index = faiss.read_index(INDEX_FILE)
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    model = SentenceTransformer(EMBEDDING_MODEL)

    # 编码查询
    query_vec = model.encode([query], normalize_embeddings=True).astype(np.float32)

    # 搜索
    scores, indices = index.search(query_vec, TOP_K)

    print(f"\n查询: \"{query}\"")
    print(f"{'=' * 60}\n")

    found = 0
    for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), 1):
        if idx < 0 or idx >= len(metadata):
            continue
        meta = metadata[idx]
        found += 1
        print(f"--- 结果 #{rank} (相似度: {score:.4f}) ---")
        print(f"  来源文件: {meta['source_file']}")
        print(f"  块类型:   {meta['chunk_type']}")
        print(f"  标题:     {meta['title']}")
        print(f"  预览:     {meta['text_preview']}")
        print()

    if found == 0:
        print("未找到匹配结果。")


if __name__ == "__main__":
    main()
