import json, os, time
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen

TZ = timezone(timedelta(hours=8))
BASE = "https://qt.gtimg.cn/q="

def _float(v):
    try: return float(v)
    except (TypeError, ValueError): return None

def _symbol(item):
    return ("sh" if item["market"] == 1 else "sz") + item["code"]

def _fetch(items):
    symbols = ",".join(_symbol(x) for x in items)
    req = Request(BASE + symbols, headers={"User-Agent":"Mozilla/5.0","Referer":"https://stockapp.finance.qq.com/"})
    last = None
    for wait in (0, 2, 5):
        if wait: time.sleep(wait)
        try:
            with urlopen(req, timeout=20) as res:
                raw = res.read().decode("gbk", errors="replace")
            rows = {}
            for line in raw.splitlines():
                if '="' not in line: continue
                symbol = line.split('="',1)[0].replace("v_","")
                values = line.split('="',1)[1].rsplit('"',1)[0].split("~")
                if len(values) < 35: continue
                rows[symbol] = values
            return rows, None
        except Exception as e: last = str(e)
    return {}, last

def _parse(item, rows, error):
    v = rows.get(_symbol(item))
    if not v:
        return {**item,"ok":False,"error":error or "quote missing","source":"tencent"}
    return {**item,"name":v[1] or item["name"],"price":_float(v[3]),"prev_close":_float(v[4]),
            "open":_float(v[5]),"volume":_float(v[6]),"change":_float(v[31]),
            "change_pct":_float(v[32]),"high":_float(v[33]),"low":_float(v[34]),
            "turnover":_float(v[37]) if len(v)>37 else None,
            "amplitude":_float(v[43]) if len(v)>43 else None,
            "turnover_rate":_float(v[38]) if len(v)>38 else None,
            "quote_time":v[30],"source":"tencent","ok":True}

def snapshot(config):
    all_items = config["indices"] + config["watchlist"]
    rows, error = _fetch(all_items)
    parsed = [_parse(x, rows, error) for x in all_items]
    n = len(config["indices"])
    return {"generated_at":datetime.now(TZ).isoformat(),"indices":parsed[:n],"watchlist":parsed[n:],
            "quality":{"ok":sum(x["ok"] for x in parsed),"total":len(parsed)}}

def load_config():
    with open(os.path.join(os.path.dirname(__file__),"..","config.json"),encoding="utf-8") as f:
        return json.load(f)
