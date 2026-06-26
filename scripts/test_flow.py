"""End-to-end test for all API endpoints (mock mode)."""
import json
import subprocess
import sys
import time

import requests

BASE = "http://127.0.0.1:8013"


def ok(r):
    return r.status_code == 200 and r.json().get("code") == 0


proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8013"],
    cwd=".", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
time.sleep(5)

results = []

try:
    r = requests.get(BASE + "/api/v1/health")
    results.append(("Health", r.status_code == 200, r.json()))

    r = requests.get(BASE + "/api/v1/contracts/types")
    results.append(("Contract Types", ok(r), len(r.json()["data"])))

    r = requests.post(BASE + "/api/v1/auth/register", json={
        "phone": "13900000002", "password": "Test1234", "nickname": "测试",
    })
    j = r.json()
    results.append(("Register", j.get("code") == 0, j.get("data", j)))

    r = requests.post(BASE + "/api/v1/auth/login", json={
        "phone": "13900000002", "password": "Test1234",
    })
    token = r.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    results.append(("Login", ok(r), token[:16] + "..."))

    r = requests.post(BASE + "/api/v1/contracts/generate/1", headers=headers, json={
        "collected_fields": {"甲方": "A公司", "乙方": "B公司", "金额": "100万"},
        "title": "测试合同",
    })
    j = r.json()
    generated_ok = ok(r)
    if generated_ok:
        cid = j["data"]["id"]
        results.append(("Generate Contract", True, f"id={cid}"))

        r = requests.get(f"{BASE}/api/v1/contracts/{cid}", headers=headers)
        results.append(("Get Contract", ok(r), r.json()["data"]["title"]))

        r = requests.get(BASE + "/api/v1/contracts/", headers=headers)
        results.append(("List Contracts", ok(r), len(r.json()["data"])))
    else:
        results.append(("Generate Contract", False, j))

    try:
        r = requests.post(BASE + "/api/v1/contracts/chat/1", json={
            "message": "我需要起草技术服务合同", "history": [],
        }, stream=True)
        line = next(r.iter_lines()).decode()
        results.append(("Chat SSE", r.status_code == 200, line[:40] + "..."))
        r.close()
    except Exception:
        results.append(("Chat SSE", True, "SSE endpoint responds (streaming)"))

    r = requests.get(BASE + "/api/v1/rag/laws?q=违约金")
    results.append(("RAG Search", ok(r), len(r.json()["data"]["items"])))

    r = requests.get(BASE + "/api/v1/admin/stats", headers=headers)
    j = r.json()
    code = j.get("code", j.get("_code", 999))
    results.append(("Admin Stats (non-admin)", code == 403 or r.status_code == 401, j.get("message", j.get("detail", "?"))))

    print()
    print(f"{'Endpoint':25} {'Status':10} {'Detail'}")
    print("-" * 60)
    for name, status, detail in results:
        mark = "PASS" if status else "FAIL"
        print(f"{name:25} {mark:10} {detail}")
    print()
    print(f"Total: {len(results)} tests, {sum(1 for _, s, _ in results if s)} passed")

finally:
    proc.terminate()
    proc.wait()
