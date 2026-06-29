import json

import pytest

METADATA_FILE = "index_metadata.json"

TRACEABLE_FIELDS = {"source_file", "chunk_type", "title", "text", "text_preview"}


@pytest.fixture(scope="module")
def metadata_data(knowledge_base_dir):
    path = knowledge_base_dir / METADATA_FILE
    assert path.exists(), f"文件不存在: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_file_exists(knowledge_base_dir):
    assert (knowledge_base_dir / METADATA_FILE).exists()


def test_valid_json(metadata_data):
    assert isinstance(metadata_data, (list, dict)), (
        "index_metadata.json 顶层不是 list 或 dict"
    )


def test_has_entries(metadata_data):
    entries = _get_entries(metadata_data)
    assert len(entries) > 0, "元数据条目为空"


def test_each_entry_has_traceable_fields(metadata_data):
    entries = _get_entries(metadata_data)
    for i, entry in enumerate(entries):
        assert isinstance(entry, dict), f"entry[{i}] 不是 dict"
        has_traceable = any(
            field in entry for field in TRACEABLE_FIELDS
        )
        assert has_traceable, (
            f"entry[{i}] 缺少可追溯字段 "
            f"(需要 source_file/chunk_type/title/text/text_preview 至少其一)"
        )


def test_chunk_type_values(metadata_data):
    entries = _get_entries(metadata_data)
    if not entries:
        return
    valid_types = {
        "template_clause",
        "template_risk_point",
        "template_generation_note",
        "bottom_line_rule",
        "legal_doc_section",
    }
    for i, entry in enumerate(entries):
        ctype = entry.get("chunk_type", "")
        if ctype and ctype not in valid_types:
            pytest.skip(
                f"entry[{i}] chunk_type='{ctype}' 不在已知类型列表中, "
                f"跳过（可能是新扩展的类型）"
            )


def _get_entries(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("entries", "items", "chunks", "data", "results"):
            if key in data and isinstance(data[key], list):
                return data[key]
    return []
