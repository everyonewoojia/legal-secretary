import pytest

BUILD_SCRIPT = "build_vector_index.py"
SEARCH_SCRIPT = "search_knowledge_base.py"


def test_build_script_exists(scripts_dir):
    path = scripts_dir / BUILD_SCRIPT
    assert path.exists(), f"脚本不存在: {path}"
    assert path.is_file()


def test_search_script_exists(scripts_dir):
    path = scripts_dir / SEARCH_SCRIPT
    assert path.exists(), f"脚本不存在: {path}"
    assert path.is_file()


def test_build_script_has_main_entry(scripts_dir):
    path = scripts_dir / BUILD_SCRIPT
    content = path.read_text(encoding="utf-8")
    assert 'if __name__ == "__main__"' in content, (
        f"{BUILD_SCRIPT}: 缺少 if __name__ == '__main__' 入口"
    )


def test_search_script_has_main_entry(scripts_dir):
    path = scripts_dir / SEARCH_SCRIPT
    content = path.read_text(encoding="utf-8")
    assert 'if __name__ == "__main__"' in content, (
        f"{SEARCH_SCRIPT}: 缺少 if __name__ == '__main__' 入口"
    )


def test_build_script_references_faiss(scripts_dir):
    path = scripts_dir / BUILD_SCRIPT
    content = path.read_text(encoding="utf-8")
    has_faiss_ref = any(
        kw in content for kw in ["faiss", "SentenceTransformer", "sentence_transformers"]
    )
    assert has_faiss_ref, (
        f"{BUILD_SCRIPT}: 未发现 faiss 或 sentence_transformers 引用"
    )


def test_search_script_has_search_logic(scripts_dir):
    path = scripts_dir / SEARCH_SCRIPT
    content = path.read_text(encoding="utf-8")
    has_search_ref = any(
        kw in content for kw in ["read_index", "index.search", "faiss"]
    )
    assert has_search_ref, (
        f"{SEARCH_SCRIPT}: 未发现 faiss 索引加载或搜索相关逻辑"
    )
