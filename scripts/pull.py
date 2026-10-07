"""只读：拉训记训练记录、身体数据、Agent 模版，存进 data/。
环境变量：XUNJI_TRAIN_KEY, XUNJI_BODY_KEY, XUNJI_TPL_KEY, DAYS（默认 4）"""
import os, time, datetime as dt
from common import post, save

SGT = dt.timezone(dt.timedelta(hours=8))
today = dt.datetime.now(SGT).date()
days = int(os.environ.get("DAYS") or 4)
tk, bk, pk = (os.environ.get(k, "") for k in ("XUNJI_TRAIN_KEY", "XUNJI_BODY_KEY", "XUNJI_TPL_KEY"))
problems = []

if tk:
    for i in range(days):
        d = (today - dt.timedelta(days=i)).isoformat()
        res = post("https://trains.xunjiapp.cn/api_trains_for_llm_v2", tk,
                   {"schema_version": "train_open_api_v2", "datestr": d, "include_full_data": True})
        body = res.get("res") if isinstance(res, dict) else None
        trains = body.get("trains") if isinstance(body, dict) else None
        if trains is None:
            problems.append(f"trains {d}: {str(res)[:200]}")
        elif trains:
            save(f"data/trains/{d}.json", body)
            print(d, len(trains), "workout(s)")
        time.sleep(2)
else:
    problems.append("XUNJI_TRAIN_KEY missing")

if bk:
    res = post("https://api.xunjiapp.cn/open/body/query_gzip", bk, {
        "start_date": (today - dt.timedelta(days=364)).isoformat(), "end_date": today.isoformat(),
        "include_latest": True, "include_records": True, "limit": 1000, "offset": 0})
    if isinstance(res, dict) and res.get("success"):
        save("data/body.json", res.get("res")); print("body ok")
    else:
        problems.append(f"body: {str(res)[:200]}")

if pk:
    res = post("https://trains.xunjiapp.cn/api_agent_templates_sync_for_llm_v2", pk, {"template_versions": {}})
    if isinstance(res, dict) and "templates" in res:
        save("data/templates.json", res); print("templates ok:", len(res["templates"]))
    else:
        problems.append(f"templates: {str(res)[:200]}")

save("data/last_pull.json", {"at": dt.datetime.now(SGT).isoformat(timespec="minutes"),
                             "days": days, "problems": problems})
print("problems:", problems or "none")
