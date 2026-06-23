import json
from diff_match_patch import diff_match_patch


def diff_text(original: str, modified: str) -> str:
    dmp = diff_match_patch()
    diffs = dmp.diff_main(original, modified)
    dmp.diff_cleanupSemantic(diffs)

    changes = []
    for op, text in diffs:
        if op == 1:
            changes.append({"type": "insert", "text": text})
        elif op == -1:
            changes.append({"type": "delete", "text": text})

    return json.dumps(changes, ensure_ascii=False)
