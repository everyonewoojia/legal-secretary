import json

import pytest

INDEX_FILE = "index.json"

REQUIRED_SOURCE_FIELDS = ["path", "type", "description", "vectorized"]


@pytest.fixture(scope="module")
def index_data(knowledge_base_dir):
    path = knowledge_base_dir / INDEX_FILE
    assert path.exists(), f"文件不存在: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_file_exists(knowledge_base_dir):
    assert (knowledge_base_dir / INDEX_FILE).exists()


def test_valid_json(index_data):
    assert isinstance(index_data, dict), "index.json 顶层不是 dict"


def _get_source_list(data):
    for key in ("sources", "files", "items", "entries", "documents"):
        if key in data and isinstance(data[key], list):
            return data[key]
    pytest.fail(
        "index.json 中未找到可识别的资源列表字段 "
        "(expected: sources/files/items/entries/documents)"
    )
    return []


def test_has_source_list(index_data):
    sources = _get_source_list(index_data)
    assert len(sources) > 0, "资源列表为空"


def test_each_source_has_required_fields(index_data, project_root):
    sources = _get_source_list(index_data)
    for i, src in enumerate(sources):
        for field in REQUIRED_SOURCE_FIELDS:
            assert field in src, (
                f"sources[{i}] 缺少字段 '{field}'"
            )


def test_vectorized_is_bool(index_data):
    sources = _get_source_list(index_data)
    for i, src in enumerate(sources):
        assert isinstance(src.get("vectorized"), bool), (
            f"sources[{i}] vectorized 不是布尔值"
        )


def test_each_path_exists(index_data, knowledge_base_dir):
    sources = _get_source_list(index_data)
    for i, src in enumerate(sources):
        rel_path = src.get("path", "")
        assert rel_path, f"sources[{i}] path 为空"
        full_path = knowledge_base_dir / rel_path
        assert full_path.exists(), (
            f"sources[{i}] path='{rel_path}' 不存在 "
            f"(预期路径: {full_path})"
        )
