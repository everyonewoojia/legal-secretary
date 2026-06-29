import json

import pytest

RULE_FILE = "bottom_line_rules.json"

REQUIRED_FIELDS = [
    "id",
    "name",
    "description",
    "applicable_contract_types",
    "trigger_keywords",
    "risk_level",
    "review_points",
    "bottom_line",
    "recommended_response",
    "negotiation_strategy",
    "demo_disclaimer",
]

VALID_RISK_LEVELS = {"high", "medium", "low"}


@pytest.fixture(scope="module")
def rules_data(clauses_dir):
    path = clauses_dir / RULE_FILE
    assert path.exists(), f"文件不存在: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_file_exists(clauses_dir):
    assert (clauses_dir / RULE_FILE).exists()


def test_valid_json(rules_data):
    assert isinstance(rules_data, dict)


def test_rules_count(rules_data):
    rules = _get_rules_list(rules_data)
    assert len(rules) >= 10, f"规则数量不足 10 条, 当前 {len(rules)} 条"


def test_each_rule_has_required_fields(rules_data):
    rules = _get_rules_list(rules_data)
    for i, rule in enumerate(rules):
        for field in REQUIRED_FIELDS:
            assert field in rule, (
                f"rules[{i}] (id={rule.get('id', '?')}) 缺少字段 '{field}'"
            )


def test_risk_level_is_valid(rules_data):
    rules = _get_rules_list(rules_data)
    for i, rule in enumerate(rules):
        level = rule.get("risk_level", "")
        assert level in VALID_RISK_LEVELS, (
            f"rules[{i}] (id={rule.get('id', '?')}) "
            f"risk_level='{level}' 不是合法的枚举值 high/medium/low"
        )


def test_negotiation_strategy_structure(rules_data):
    rules = _get_rules_list(rules_data)
    expected_positions = {"firm_position", "compromise_position", "fallback_position"}
    for i, rule in enumerate(rules):
        strategy = rule.get("negotiation_strategy", {})
        for pos in expected_positions:
            assert pos in strategy, (
                f"rules[{i}] (id={rule.get('id', '?')}) "
                f"negotiation_strategy 缺少 '{pos}'"
            )
        for pos in expected_positions:
            pos_data = strategy.get(pos, {})
            assert "script" in pos_data, (
                f"rules[{i}] (id={rule.get('id', '?')}) "
                f"negotiation_strategy.{pos} 缺少 'script'"
            )


def test_demo_disclaimer(rules_data):
    rules = _get_rules_list(rules_data)
    for i, rule in enumerate(rules):
        disclaimer = rule.get("demo_disclaimer", "")
        assert any(
            kw in disclaimer for kw in ["实训 Demo", "不替代专业律师意见"]
        ), (
            f"rules[{i}] (id={rule.get('id', '?')}) "
            f"demo_disclaimer 缺少实训字样"
        )


def _get_rules_list(rules_data):
    if "rules" in rules_data:
        return rules_data["rules"]
    if "items" in rules_data:
        return rules_data["items"]
    pytest.fail("规则数据中未找到 'rules' 或 'items' 字段")
    return []
