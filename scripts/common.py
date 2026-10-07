import json, time, gzip, os, urllib.request, urllib.error

def post(url, key, body, retries=4):
    data = json.dumps(body, ensure_ascii=False).encode()
    for i in range(retries):
        req = urllib.request.Request(url, data=data, method="POST", headers={
            "Authorization": "Bearer " + key, "Content-Type": "application/json",
            "Accept-Encoding": "gzip"})
        try:
            r = urllib.request.urlopen(req, timeout=60); raw = r.read()
        except urllib.error.HTTPError as e:
            raw = e.read()
        if raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
        try:
            res = json.loads(raw.decode())
        except Exception:
            res = {"success": False, "res": raw.decode(errors="replace")[:300]}
        msg = json.dumps(res, ensure_ascii=False)[:300]
        if "too frequent" in msg:
            wait = 20
            if isinstance(res, dict) and res.get("retry_after_ms"):
                wait = res["retry_after_ms"] / 1000 + 1
            print("  too frequent, wait", wait); time.sleep(wait); continue
        return res
    return res

def save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=True)
