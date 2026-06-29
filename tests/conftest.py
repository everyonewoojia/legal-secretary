import json
import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def project_root():
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def knowledge_base_dir(project_root):
    return project_root / "knowledge_base"


@pytest.fixture(scope="session")
def templates_dir(knowledge_base_dir):
    return knowledge_base_dir / "templates"


@pytest.fixture(scope="session")
def legal_docs_dir(knowledge_base_dir):
    return knowledge_base_dir / "legal_docs"


@pytest.fixture(scope="session")
def clauses_dir(knowledge_base_dir):
    return knowledge_base_dir / "clauses"


@pytest.fixture(scope="session")
def scripts_dir(project_root):
    return project_root / "scripts"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
