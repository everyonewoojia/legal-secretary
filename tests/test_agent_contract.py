"""测试 contract_agent.py 的模板文件映射

验证 TEMPLATE_FILE_MAP 中的 5 类映射文件真实存在，
验证未知合同类型能抛出清晰异常。
不依赖外部网络，不加载 LLM 模型。
"""

import os
import sys

import pytest

# 添加 backend 到 sys.path 以便 agent/contract_agent.py 的导入链能找到 app.*
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_backend_dir = os.path.join(_project_root, "backend")
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from agent.contract_agent import ContractAgent

TEMPLATES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "knowledge_base",
    "templates",
)

EXPECTED_MAPPINGS = {
    "tech_service": "technical_service_contract.json",
    "procurement": "purchase_contract.json",
    "employment": "labor_contract.json",
    "cooperation": "cooperation_agreement.json",
    "non_disclosure": "nda_contract.json",
}


def test_template_file_map_keys():
    """TEMPLATE_FILE_MAP 包含 5 类合同"""
    assert len(ContractAgent.TEMPLATE_FILE_MAP) == 5
    for code in EXPECTED_MAPPINGS:
        assert code in ContractAgent.TEMPLATE_FILE_MAP, (
            f"TEMPLATE_FILE_MAP 缺少 '{code}'"
        )


def test_all_mapped_files_exist():
    """TEMPLATE_FILE_MAP 中每个映射文件在磁盘上真实存在"""
    for code, filename in ContractAgent.TEMPLATE_FILE_MAP.items():
        filepath = os.path.join(TEMPLATES_DIR, filename)
        assert os.path.isfile(filepath), (
            f"类型 '{code}' 映射的文件 '{filename}' 不存在 "
            f"(预期路径: {filepath})"
        )


def test_unknown_type_raises():
    """未知合同类型抛出 FileNotFoundError 并包含支持列表"""
    agent = ContractAgent()
    with pytest.raises(FileNotFoundError) as exc:
        agent._load_template("nonexistent_type")
    msg = str(exc.value)
    assert "未知合同类型" in msg
    assert "nonexistent_type" in msg
    for code in EXPECTED_MAPPINGS:
        assert code in msg


def test_known_type_does_not_raise():
    """已知合同类型不抛出异常"""
    agent = ContractAgent()
    for code in ContractAgent.TEMPLATE_FILE_MAP:
        try:
            result = agent._load_template(code)
            assert isinstance(result, list)
        except FileNotFoundError:
            pytest.fail(f"已知类型 '{code}' 不应抛出 FileNotFoundError")
