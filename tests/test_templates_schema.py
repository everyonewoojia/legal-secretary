import json

import pytest

TEMPLATE_FILES = [
    "technical_service_contract.json",
    "purchase_contract.json",
    "labor_contract.json",
    "cooperation_agreement.json",
    "nda_contract.json",
]

EXPECTED_FIELDS = [
    "contract_type",
    "display_name",
    "description",
    "required_fields",
    "sections",
    "clauses",
    "risk_points",
    "generation_notes",
]

CLAUSE_REQUIRED_FIELDS = ["id", "title", "content", "variables", "risk_tips"]


@pytest.mark.parametrize("filename", TEMPLATE_FILES)
def test_template_exists(templates_dir, filename):
    path = templates_dir / filename
    assert path.exists(), f"模板文件不存在: {path}"
    assert path.is_file()


@pytest.mark.parametrize("filename", TEMPLATE_FILES)
def test_template_valid_json(templates_dir, filename):
    path = templates_dir / filename
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict), f"{filename}: JSON 顶层不是 dict"


@pytest.mark.parametrize("filename", TEMPLATE_FILES)
def test_template_has_required_fields(templates_dir, filename):
    path = templates_dir / filename
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for field in EXPECTED_FIELDS:
        assert field in data, f"{filename}: 缺少字段 '{field}'"


@pytest.mark.parametrize("filename", TEMPLATE_FILES)
def test_template_has_non_empty_clauses(templates_dir, filename):
    path = templates_dir / filename
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    clauses = data.get("clauses", [])
    assert isinstance(clauses, list), f"{filename}: clauses 不是 list"
    assert len(clauses) > 0, f"{filename}: clauses 为空"


@pytest.mark.parametrize("filename", TEMPLATE_FILES)
def test_template_clause_structure(templates_dir, filename):
    path = templates_dir / filename
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for i, clause in enumerate(data.get("clauses", [])):
        for field in CLAUSE_REQUIRED_FIELDS:
            assert field in clause, (
                f"{filename}: clauses[{i}] 缺少字段 '{field}'"
            )
        variables = clause.get("variables", None)
        assert isinstance(variables, list), (
            f"{filename}: clauses[{i}].variables 不是数组"
        )


@pytest.mark.parametrize("filename", TEMPLATE_FILES)
def test_template_clause_risk_tips_non_empty(templates_dir, filename):
    path = templates_dir / filename
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for i, clause in enumerate(data.get("clauses", [])):
        risk_tips = clause.get("risk_tips", "")
        assert risk_tips and risk_tips.strip(), (
            f"{filename}: clauses[{i}].risk_tips 为空"
        )
