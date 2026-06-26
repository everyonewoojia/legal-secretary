import difflib


def compute_diff(old_text: str, new_text: str) -> list[dict]:
    diff = difflib.unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
    )
    changes = []
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            changes.append({"type": "addition", "content": line[1:].rstrip()})
        elif line.startswith("-") and not line.startswith("---"):
            changes.append({"type": "deletion", "content": line[1:].rstrip()})
    return changes
