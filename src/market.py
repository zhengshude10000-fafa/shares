import json, os, time
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen

TZ = timezone(timedelta(hours=8))
BASE = "https://push2.eastmoney.com/api/qt/stock/get"
FIELDS = "f43,f44,f45,f46,f47,f48,f49,f50,f57,f58,f60,f116,f117,f162,f167,f168,f169,f170,f171"

def _num(v, scale=100):
    if v in (None, "-"): return None
    return round(float(v) / scale, 3)

def quote(item):
    last = None
    for wait in (0, 2, 5):
        if wait: time.sleep(wait)
        try:
            url=BASE+"?"+urlencode({"secid":f"{item['market']}.{item['code']}","fields":FIELDS})
            req=Request(url,headers={"User-Agent":"Mozilla/5.0","Referer":"https://quote.eastmoney.com/"})
            with urlopen(req,timeout=12) as res:d=json.loads(res.read().decode("utf-8")).get("data")
            if not d: raise RuntimeError("empty quote")
            return {**item,"price":_num(d.get("f43")),"open":_num(d.get("f46")),"high":_num(d.get("f44")),
                    "low":_num(d.get("f45")),"prev_close":_num(d.get("f60")),"change_pct":_num(d.get("f170")),
                    "turnover":d.get("f48"),"volume":d.get("f47"),"amplitude":_num(d.get("f171")),
                    "turnover_rate":_num(d.get("f168")),"pe":_num(d.get("f162")),"pb":_num(d.get("f167")),
                    "source":"eastmoney","ok":True}
        except Exception as e: last = str(e)
    return {**item,"ok":False,"error":last,"source":"eastmoney"}

def snapshot(config):
    indices=[quote(x) for x in config["indices"]]
    watch=[quote(x) for x in config["watchlist"]]
    return {"generated_at":datetime.now(TZ).isoformat(),"indices":indices,"watchlist":watch,
            "quality":{"ok":sum(x["ok"] for x in indices+watch),"total":len(indices)+len(watch)}}

def load_config():
    with open(os.path.join(os.path.dirname(__file__),"..","config.json"),encoding="utf-8") as f:return json.load(f)
