#!/usr/bin/env python3
"""Independent pure-Python reference for the parity bench (assets/spm-live.js).

Same definitions, written separately: the legacy warehouse, the seven constructed drifts planted one
at a time, the five checks (counts, keys, daily exact, monthly parity bar, time-zone edge), the
ladder of rungs, the loose bar and the break mode. Prints the canon as JSON in the same shape as
materials/run_ladder_node.js (minus the selfTest keys). compare-ladder.py checks the two by value.

Usage: python3 -I materials/spm_reference.py
"""
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LATE_DAYS = 30
EDGE_MIN = 60
METRICS = ["orders", "itemValue", "freight", "itemsPerOrder", "reviewed", "avgReview"]
BAR = {"orders": ("abs", 0), "itemValue": ("rel", 0.0005), "freight": ("rel", 0.0005),
       "itemsPerOrder": ("abs", 0.005), "reviewed": ("abs", 0), "avgReview": ("abs", 0.01)}
LOOSE = {m: ("rel", 0.03) for m in METRICS}
DRIFTS = [("late", "defect"), ("tz", "defect"), ("nul", "defect"), ("idiv", "defect"), ("case", "defect"),
          ("round", "accepted"), ("float", "accepted")]
RUNGS = [["counts"], ["counts", "keys"], ["counts", "keys", "daily"], ["counts", "keys", "parity"],
         ["counts", "keys", "parity", "edge"]]
DAY0 = datetime.date(2016, 9, 1)


def load():
    with open(os.path.join(HERE, "spm-sample.json")) as f:
        D = json.load(f)
    day, s = [], 0
    for x in D["dayDelta"]:
        s += x
        day.append(s)
    D["_day"] = day
    return D


def in_dst(D, d):
    return any(a <= d <= b for a, b in D["dstWindows"])


def legacy(D):
    rows = [dict(k=k, day=D["_day"][k], mod=D["mod"][k], exp=D["exp"][k], items=D["items"][k], gmv=D["gmv"][k],
                 fr=D["fr"][k], rev=D["review"][k], fk=1) for k in range(D["nOrders"])]
    return {"rows": rows, "idiv": False, "float": False}


def new_wh(D, drift):
    on = lambda i: drift == i or drift == "all"
    rows = []
    for r in legacy(D)["rows"]:
        r = dict(r)
        if on("tz") and in_dst(D, r["day"]) and r["mod"] < 60:
            r["day"] -= 1
        if on("nul") and r["rev"] is None:
            r["rev"] = 0
        if on("case") and r["exp"] == 2:
            r["fk"] = 0
        if on("round") and r["items"] > 1:
            n = r["items"]
            r["fr"] = n * ((2 * r["fr"] + n) // (2 * n))
        rows.append(r)
    if on("late"):
        rows = rows + [dict(r) for r in rows if D["deliv"][r["k"]] is not None and D["deliv"][r["k"]] > LATE_DAYS]
    return {"rows": rows, "idiv": on("idiv"), "float": on("float")}


def month_of(d):
    t = DAY0 + datetime.timedelta(days=d)
    return "%04d-%02d" % (t.year, t.month)


def aggregate(W, grain):
    B = {}
    for r in W["rows"]:
        key = str(r["day"]) if grain == "day" else month_of(r["day"])
        b = B.setdefault(key, {"n": 0, "items": 0, "gmvC": 0, "frC": 0, "gmvF": 0.0, "frF": 0.0, "revN": 0, "revS": 0})
        b["n"] += 1
        b["items"] += r["items"]
        b["gmvC"] += r["gmv"]
        b["frC"] += r["fr"]
        b["gmvF"] += r["gmv"] / 100
        b["frF"] += r["fr"] / 100
        if r["rev"] is not None:
            b["revN"] += 1
            b["revS"] += r["rev"]
    out = {}
    for key, b in B.items():
        out[key] = {
            "orders": b["n"],
            "itemValue": b["gmvF"] if W["float"] else b["gmvC"] / 100,
            "freight": b["frF"] if W["float"] else b["frC"] / 100,
            "itemsPerOrder": (b["items"] // b["n"] if W["idiv"] else b["items"] / b["n"]) if b["n"] else None,
            "reviewed": b["revN"],
            "avgReview": b["revS"] / b["revN"] if b["revN"] else None,
        }
    return out


EMPTY = {"orders": 0, "itemValue": 0, "freight": 0, "itemsPerOrder": None, "reviewed": 0, "avgReview": None}


def differs(a, b, rule):
    if a is None and b is None:
        return False
    if a is None or b is None:
        return True
    if rule is None:
        return a != b
    kind, tol = rule
    d = abs(a - b)
    return d > tol if kind == "abs" else d > tol * abs(a)


def compare_agg(LA, NA, grain, bar):
    keys = set(LA) | set(NA)
    keys = sorted(keys, key=int) if grain == "day" else sorted(keys)
    out = {m: {"fail": 0, "maxGap": 0} for m in METRICS}
    for k in keys:
        a, b = LA.get(k, EMPTY), NA.get(k, EMPTY)
        for m in METRICS:
            x, y = a[m], b[m]
            if differs(x, y, bar[m] if bar else None):
                out[m]["fail"] += 1
            if x is not None and y is not None:
                out[m]["maxGap"] = max(out[m]["maxGap"], abs(x - y))
    failing = sum(out[m]["fail"] for m in METRICS)
    return {"buckets": len(keys), "metrics": out, "failing": failing, "alarm": failing > 0}


def key_side(W, n):
    cnt, fk = [0] * n, 0
    for r in W["rows"]:
        if cnt[r["k"]] == 0 and not r["fk"]:
            fk += 1
        cnt[r["k"]] += 1
    return cnt, sum(1 for c in cnt if c > 1), fk


def check_keys(L, N, n):
    ca, da, fa = key_side(L, n)
    cb, db, fb = key_side(N, n)
    missing = sum(1 for k in range(n) if ca[k] > 0 and cb[k] == 0)
    extra = sum(1 for k in range(n) if cb[k] > 0 and ca[k] == 0)
    return {"missing": missing, "extra": extra, "dupLegacy": da, "duplicated": db, "unresolvedLegacy": fa,
            "unresolvedNew": fb, "alarm": missing > 0 or extra > 0 or da != db or fa != fb}


def check_edge(L, N):
    first = {}
    for r in N["rows"]:
        first.setdefault(r["k"], r["day"])
    near = mism = 0
    for r in L["rows"]:
        if r["mod"] < EDGE_MIN or r["mod"] >= 1440 - EDGE_MIN:
            near += 1
            if r["k"] in first and first[r["k"]] != r["day"]:
                mism += 1
    return {"near": near, "mismatched": mism, "alarm": mism > 0}


def totals(W):
    rows = [dict(r, day=0) for r in W["rows"]]
    a = aggregate({"rows": rows, "idiv": W["idiv"], "float": W["float"]}, "month")
    return a[next(iter(a))]


def detail(D, L, N, loose):
    return {
        "counts": {"legacy": len(L["rows"]), "fresh": len(N["rows"]), "alarm": len(L["rows"]) != len(N["rows"])},
        "keys": check_keys(L, N, D["nOrders"]),
        "daily": compare_agg(aggregate(L, "day"), aggregate(N, "day"), "day", None),
        "parity": compare_agg(aggregate(L, "month"), aggregate(N, "month"), "month", LOOSE if loose else BAR),
        "edge": check_edge(L, N),
        "totals": {"legacy": totals(L), "fresh": totals(N)},
    }


def score(dets, rung):
    checks = RUNGS[rung]
    out = {"caught": 0, "missed": 0, "falseAlarms": 0, "quiet": 0, "verdicts": {}}
    kinds = dict(DRIFTS)
    kinds["none"] = "control"
    for i in ["none"] + [d for d, _ in DRIFTS]:
        fired = [c for c in checks if dets[i][c]["alarm"]]
        if kinds[i] == "defect":
            v = "caught" if fired else "missed"
            out["caught" if fired else "missed"] += 1
        else:
            v = "false alarm" if fired else "quiet"
            out["falseAlarms" if fired else "quiet"] += 1
        out["verdicts"][i] = {"verdict": v, "fired": fired}
    return out


def run(D, mode):
    L = legacy(D)
    dets = {}
    for i in ["none"] + [d for d, _ in DRIFTS]:
        N = new_wh(D, i)
        dets[i] = detail(D, N, N, False) if mode == "break" else detail(D, L, N, mode == "loose")
    NA = new_wh(D, "all")
    allv = detail(D, NA, NA, False) if mode == "break" else detail(D, L, NA, mode == "loose")
    return {"mode": mode, "perDrift": dets, "all": allv, "rungs": [score(dets, r) for r in range(len(RUNGS))]}


def touched(D, i):
    c = 0
    for k in range(D["nOrders"]):
        it, dl = D["items"][k], D["deliv"][k]
        if i == "late" and dl is not None and dl > LATE_DAYS:
            c += 1
        elif i == "tz" and in_dst(D, D["_day"][k]) and D["mod"][k] < 60:
            c += 1
        elif i == "nul" and D["review"][k] is None:
            c += 1
        elif i == "case" and D["exp"][k] == 2:
            c += 1
        elif i == "round" and it > 1 and it * ((2 * D["fr"][k] + it) // (2 * it)) != D["fr"][k]:
            c += 1
        elif i in ("idiv", "float"):
            c += 1
    return c


def main():
    D = load()
    ref = dict(D["reference"])
    out = {"normal": run(D, "normal"), "loose": run(D, "loose"), "brk": run(D, "break"),
           "touched": {d: touched(D, d) for d, _ in DRIFTS}, "reference": ref, "lateDays": LATE_DAYS}
    print(json.dumps(out))


if __name__ == "__main__":
    main()
