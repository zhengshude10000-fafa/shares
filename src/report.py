import json, os, sys
from datetime import datetime, timezone, timedelta
from market import snapshot, load_config

TZ=timezone(timedelta(hours=8)); ROOT=os.path.dirname(os.path.dirname(__file__)); REPORTS=os.path.join(ROOT,"reports")

def trading_day(now): return now.weekday()<5
def fmt(x,suffix=""): return "数据缺失" if x is None else f"{x:+.2f}{suffix}"

def classify(q):
    p=q.get("change_pct")
    if p is None:return "数据缺失，禁止推断"
    if p>=5:return "强势，但防止高开回落"
    if p>=2:return "偏强，观察量价能否延续"
    if p<=-5:return "显著走弱，优先控制风险"
    if p<=-2:return "偏弱，等待止跌确认"
    return "震荡，等待方向选择"

def common(data,kind):
    now=datetime.now(TZ); qs=[q for q in data["watchlist"] if q.get("ok")]
    ranked=sorted(qs,key=lambda x:x.get("change_pct") or -999,reverse=True)
    idx=[{"name":q["name"],"change_pct":q.get("change_pct"),"view":classify(q)} for q in data["indices"]]
    watch=[{"code":q["code"],"name":q["name"],"industry":q.get("industry"),"price":q.get("price"),
            "change_pct":q.get("change_pct"),"view":classify(q)} for q in ranked]
    missing=data["quality"]["total"]-data["quality"]["ok"]
    return {"schema_version":1,"type":kind,"date":now.strftime("%Y-%m-%d"),"generated_at":data["generated_at"],
            "is_trading_day":trading_day(now),"data_quality":{**data["quality"],"warning":f"{missing}项数据缺失" if missing else "数据完整"},
            "indices":idx,"watchlist":watch,"disclaimer":"仅供个人观察与复盘，不构成投资建议。"}

def build(kind,data):
    r=common(data,kind); ranked=r["watchlist"]
    if kind=="pre-market":
        r.update({"title":"A股盘前观察","market_summary":"基于最近可用行情生成条件式计划；09:00版本不包含当日集合竞价。",
          "sector_observation":group(ranked),"focus":[{**x,"condition":"仅在板块同步、量价确认且未明显高开时观察"} for x in ranked[:5]],
          "risks":["盘前数据可能为上一交易日收盘快照","高开不追，弱于板块时降低优先级","数据缺失项目不作方向判断"],
          "next_actions":["09:25后核对集合竞价与板块联动","开盘后观察15–30分钟承接","触发风险条件时优先控制仓位"]})
    else:
        up=sum((x.get("change_pct") or 0)>0 for x in ranked); down=sum((x.get("change_pct") or 0)<0 for x in ranked)
        r.update({"title":"A股盘后复盘","market_summary":f"自选样本上涨{up}只、下跌{down}只；结合指数强弱判断风险偏好。",
          "sector_observation":group(ranked),"focus":ranked[:5],
          "risks":["单一数据源可能延迟或调整字段","资金流数据不作为单独买卖依据","大幅波动标的次日注意兑现压力"],
          "next_actions":[f"关注{x['name']}：{x['view']}" for x in ranked[:5]]})
    return r

def group(items):
    out={}
    for x in items:out.setdefault(x.get("industry") or "未分类",[]).append(x["name"])
    return [{"sector":k,"symbols":v,"note":"观察板块内个股是否形成同步强弱"} for k,v in out.items()]

def main():
    kind=sys.argv[1] if len(sys.argv)>1 else "after-market"
    if kind not in ("pre-market","after-market"):raise SystemExit("kind must be pre-market or after-market")
    data=snapshot(load_config()); report=build(kind,data); os.makedirs(REPORTS,exist_ok=True)
    latest=os.path.join(REPORTS,f"{kind}-latest.json"); dated=os.path.join(REPORTS,f"{kind}-{report['date']}.json")
    for p in (latest,dated):
        with open(p,"w",encoding="utf-8") as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print(latest)
if __name__=="__main__":main()
