import json
import os


async def retrieve(query: str, contract_type: str = "", top_k: int = 3) -> list[dict]:
    templates_dir = "knowledge_base/templates"
    results = []

    if os.path.exists(templates_dir):
        for fname in os.listdir(templates_dir):
            if fname.endswith(".json"):
                with open(os.path.join(templates_dir, fname), "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        if not contract_type or data.get("type") == contract_type:
                            results.append({
                                "source": fname,
                                "content": json.dumps(data, ensure_ascii=False)[:500],
                                "score": 0.85,
                            })
                    except json.JSONDecodeError:
                        continue

    return results[:top_k]
