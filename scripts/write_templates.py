"""写入 Agent 模版：读 templates/payload.json（upserts 只需 name + movements）。
同名模版自动转成更新（带 template_id/base_version）；deletes 写模版名。
训记不认识的动作名会被去掉并报告。"""
import json, os, re, time
from common import post, save

KEY = os.environ["XUNJI_TPL_KEY"]
BASE = "https://trains.xunjiapp.cn"
spec = json.load(open("templates/payload.json", encoding="utf-8"))
sync = post(BASE + "/api_agent_templates_sync_for_llm_v2", KEY, {"template_versions": {}})
existing = {t.get("name"): t for t in sync.get("templates", [])}
print("existing:", list(existing))

def tid(t): return t.get("template_id") or t.get("unique_id") or t.get("id")
def ver(t): return t.get("version") or t.get("base_version")

body = {"confirmed": True, "upserts": [], "deletes": []}
for u in spec.get("upserts", []):
    u = dict(u)
    if u["name"] in existing:
        t = existing[u["name"]]
        u.pop("client_id", None); u["template_id"] = tid(t); u["base_version"] = ver(t)
    body["upserts"].append(u)
for name in spec.get("deletes", []):
    if name in existing:
        t = existing[name]; body["deletes"].append({"template_id": tid(t), "base_version": ver(t)})
if spec.get("folder_name"):
    body["folder_update"] = {"name": spec["folder_name"], "base_version": sync["folder"]["version"]}

sha = (os.environ.get("GITHUB_SHA") or str(int(time.time())))[:10]
dropped = []
for attempt in range(1, 16):
    body["mutation_id"] = f"gh-{sha}-{attempt}"
    res = post(BASE + "/api_agent_templates_mutate_for_llm_v1", KEY, body)
    if res.get("success") or res.get("applied"):
        print("OK:", [a.get("data", {}).get("name") for a in res.get("applied", [])]); break
    msg = str(res.get("res", res))
    m = re.search(r"movement not found:\s*(.+)", msg)
    if m:
        n = m.group(1).strip(); dropped.append(n); print("drop unknown movement:", n)
        for u in body["upserts"]:
            u["movements"] = [x for x in u.get("movements", []) if x.get("name") != n]
        time.sleep(16); continue
    print("FAILED:", msg[:500]); break
save("data/last_write.json", {"sha": sha, "dropped": dropped, "result": res})
