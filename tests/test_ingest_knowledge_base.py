"""测试 ingest_knowledge_base.py 的 chunk 提取函数

仅测试文件级分块逻辑，不测试数据库写入（需真实 SQLite 连接）。
不依赖外部资源，不修改数据库。
"""

import json
import os
import tempfile

import pytest

from scripts.ingest_knowledge_base import (
    chunk_bottom_line_rules,
    chunk_markdown,
    chunk_template_json,
    _extract_item_chunks,
)


def test_chunk_markdown_simple():
    """Markdown 按 ## 分块"""
    content = "# 标题\n\n## 第一节\n内容A\n\n## 第二节\n内容B"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(content)
        path = f.name
    try:
        chunks = chunk_markdown(path, "test.md")
        assert len(chunks) >= 1
        for c in chunks:
            assert "source" in c
            assert "content" in c
            assert "category" in c
            assert c["category"] == "legal_doc"
    finally:
        os.unlink(path)


def test_chunk_template_json_dict():
    """模板 JSON 顶层为 dict 时正常提取"""
    data = {
        "contract_type": "test_type",
        "display_name": "测试合同",
        "clauses": [
            {"id": "c1", "title": "条款1", "content": "内容1", "variables": [], "risk_tips": "注意"},
        ],
        "sections": [
            {"title": "章节1", "content_template": "模板内容"},
        ],
        "risk_points": [
            {"risk_type": "风险1", "risk_description": "描述", "suggestion": "建议"},
        ],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        path = f.name
    try:
        chunks = chunk_template_json(path, "test/template.json")
        clause_chunks = [c for c in chunks if "template_clause" in c["category"]]
        section_chunks = [c for c in chunks if "template_section" in c["category"]]
        risk_chunks = [c for c in chunks if "template_risk" in c["category"]]
        assert len(clause_chunks) == 1
        assert len(section_chunks) == 1
        assert len(risk_chunks) == 1
    finally:
        os.unlink(path)


def test_chunk_template_json_list():
    """模板 JSON 顶层为 list 时也能正常提取"""
    items = [
        {
            "contract_type": "type_a",
            "display_name": "合同A",
            "clauses": [
                {"id": "c1", "title": "条款A1", "content": "内容A1", "variables": [], "risk_tips": "注意"},
            ],
            "sections": [],
            "risk_points": [],
        },
        {
            "contract_type": "type_b",
            "display_name": "合同B",
            "clauses": [
                {"id": "c2", "title": "条款B1", "content": "内容B1", "variables": [], "risk_tips": "风险"},
            ],
            "sections": [],
            "risk_points": [],
        },
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False)
        path = f.name
    try:
        chunks = chunk_template_json(path, "test/list_template.json")
        assert len(chunks) == 2
    finally:
        os.unlink(path)


def test_chunk_template_json_non_dict_non_list():
    """JSON 顶层既不是 dict 也不是 list 时，返回空列表"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump("just a string", f, ensure_ascii=False)
        path = f.name
    try:
        chunks = chunk_template_json(path, "test/str.json")
        assert chunks == []
    finally:
        os.unlink(path)


def test_chunk_bottom_line_rules_dict():
    """底线规则 JSON 顶层为 dict（含 rules 列表）"""
    data = {
        "meta": {"title": "规则库"},
        "rules": [
            {
                "id": "rule_001",
                "name": "管辖法院变更",
                "description": "对方变更管辖法院",
                "risk_level": "high",
                "trigger_keywords": ["管辖", "法院"],
                "bottom_line": "不接受",
                "recommended_response": "拒绝",
                "negotiation_strategy": {
                    "firm_position": {"title": "强硬", "script": "我方要求不变"},
                    "compromise_position": {"title": "折中", "script": "可协商"},
                    "fallback_position": {"title": "底线", "script": "必须对等"},
                },
            },
        ],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        path = f.name
    try:
        chunks = chunk_bottom_line_rules(path, "clauses/bottom_line_rules.json")
        assert len(chunks) == 1
        assert "管辖法院变更" in chunks[0]["content"]
        assert "high" in chunks[0]["category"]
        assert "我方要求不变" in chunks[0]["content"]
    finally:
        os.unlink(path)


def test_chunk_bottom_line_rules_list():
    """底线规则 JSON 顶层为 list"""
    rules = [
        {
            "id": "rule_001",
            "name": "规则一",
            "description": "描述一",
            "risk_level": "medium",
            "trigger_keywords": ["关键词"],
            "bottom_line": "底线一",
            "recommended_response": "响应一",
            "negotiation_strategy": {},
        },
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False)
        path = f.name
    try:
        chunks = chunk_bottom_line_rules(path, "clauses/bottom_line_rules.json")
        assert len(chunks) == 1
    finally:
        os.unlink(path)


def test_chunk_bottom_line_rules_empty():
    """底线规则 JSON 无有效规则时返回空"""
    data = {"meta": {}, "rules": []}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        path = f.name
    try:
        chunks = chunk_bottom_line_rules(path, "clauses/bottom_line_rules.json")
        assert chunks == []
    finally:
        os.unlink(path)


def test_extract_item_chunks():
    """_extract_item_chunks 从 dict item 正确提取 clauses/sections/risk_points"""
    item = {
        "contract_type": "test",
        "display_name": "测试",
        "clauses": [
            {"id": "c1", "title": "条款", "content": "内容", "variables": [], "risk_tips": "风险提示"},
        ],
        "sections": [
            {"title": "章节", "content_template": "模板xxx"},
        ],
        "risk_points": [
            {"risk_type": "R1", "risk_description": "描述", "suggestion": "建议"},
        ],
    }
    chunks = _extract_item_chunks(item, "test.json")
    assert len(chunks) == 3
    categories = {c["category"] for c in chunks}
    assert "template_clause|test" in categories
    assert "template_section|test" in categories
    assert "template_risk|test" in categories
