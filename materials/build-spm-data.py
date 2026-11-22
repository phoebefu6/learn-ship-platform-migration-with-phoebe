#!/usr/bin/env python3
"""Build the parity-bench data for learn-ship-platform-migration-with-phoebe.

Internal build script. Not linked from any audience-facing page.

Usage
-----
  python3 -I materials/build-spm-data.py <dir-with-olist-csvs> [--write]

The directory holds the Kaggle CSVs of the Brazilian E-Commerce Public Dataset by Olist
(CC BY-NC-SA 4.0). No-login route: kagglehub.dataset_download("olistbr/brazilian-ecommerce").

Step 1 reproduces the 8,614-order frame of learn-ship-ecommerce-enabler-with-phoebe and
learn-ship-social-commerce-with-phoebe (delivered orders, seed 20260929, 250 of the repeat customers
plus one-timers at the real ratio, three marketplace exports split 45/35/20) and ASSERTS it:
8,333 customers, 8,614 orders, 9,843 lines, exports 3,935 / 2,912 / 1,767. The random draws are
replayed in the same order as the sibling builders so the export split is identical.

Step 2 ships what the parity bench needs, all DERIVED and MASKED (no Olist id, no text):
  per order, in purchase order: purchase day (running delta from 2016-09-01) and minute of the day
  (Olist purchase timestamps, read as Sao Paulo civil time), export, items, item value and freight in
  cents, the first review SCORE or null, and days from purchase to delivery.
  The daylight-saving windows of America/Sao_Paulo over the sample, from the IANA tz database
  (python zoneinfo), as day-index ranges. The builder asserts that the engine's window rule gives the
  same shifted orders as a direct zoneinfo conversion of every timestamp.
  Reference totals computed here with pandas on the source rows (an independent code path).

The legacy/new split, the drifts and the parity bar are CONSTRUCTED in the engine
(assets/spm-live.js) and labelled on the widget. Nothing random is shipped: every drift is a
deterministic rule on real rows.

Output: assets/spm-sample.js (window.SPM_DATA = <json>) and materials/spm-sample.json, same payload,
serialised with json.dumps.
"""
import json
import math
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- sibling frame (do not change)
SEED = 20260929
N_REPEAT = 250
EXPORT_SHARE = [0.45, 0.35, 0.20]
FIRST = ["Ana", "Maria", "Joao", "Pedro", "Lucas", "Julia", "Mariana", "Gabriel", "Rafael", "Beatriz",
         "Carlos", "Fernanda", "Paulo", "Camila", "Bruno", "Larissa", "Felipe", "Amanda", "Rodrigo",
         "Leticia", "Marcos", "Patricia", "Thiago", "Aline", "Diego", "Renata", "Eduardo", "Vanessa",
         "Gustavo", "Bianca", "Daniel", "Carolina", "Vinicius", "Tatiana", "Leonardo", "Priscila",
         "Ricardo", "Natalia", "Andre", "Isabela"]
LAST = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira", "Lima",
        "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida", "Lopes", "Soares", "Fernandes",
        "Vieira", "Barbosa", "Rocha", "Dias", "Nascimento", "Andrade", "Moreira", "Nunes", "Marques",
        "Machado", "Mendes", "Freitas"]
EXPECT = {"customers": 8333, "orders": 8614, "lines": 9843, "exports": [3935, 2912, 1767]}
EXPORTS = ["Export A", "Export B", "Export C"]
DAY0 = pd.Timestamp("2016-09-01")
TZ = ZoneInfo("America/Sao_Paulo")


def frame(o, c, it):
    """Replay the sibling builder's draws in the same order; return the sorted order frame + exports."""
    o = o[o.order_status == "delivered"].merge(c, on="customer_id")
    per = o.groupby("customer_unique_id").order_id.nunique()
    rep = np.sort(per[per > 1].index.values)
    one = np.sort(per[per == 1].index.values)
    n_one = int(round(N_REPEAT * len(one) / len(rep)))
    rng = np.random.default_rng(SEED)
    pick = np.concatenate([rng.choice(rep, N_REPEAT, replace=False), rng.choice(one, n_one, replace=False)])
    pick = sorted(pick.tolist())
    so = o[o.customer_unique_id.isin(set(pick))].sort_values(
        ["order_purchase_timestamp", "order_id"]).reset_index(drop=True)
    fw = np.array([1 / (k + 1) for k in range(len(FIRST))]); fw /= fw.sum()
    lw = np.array([1 / (k + 1) for k in range(len(LAST))]); lw /= lw.sum()
    for _ in pick:                       # the sibling's synthetic names: replayed only to keep the stream
        rng.choice(len(FIRST), p=fw); rng.choice(len(LAST), p=lw)
    rng.integers(0, 100, len(pick))      # the sibling's synthetic phone digits, same reason
    exp = rng.choice(3, len(so), p=EXPORT_SHARE).tolist()
    li = it[it.order_id.isin(set(so.order_id))]
    got = {"customers": len(pick), "orders": len(so), "lines": len(li),
           "exports": [exp.count(i) for i in range(3)]}
    assert got == EXPECT, f"8,614 frame NOT reproduced: {got} vs {EXPECT}"
    print("frame reproduced:", got)
    return so, exp, pick


def dst_at(local_naive):
    """True when Sao Paulo civil time `local_naive` is in daylight saving (fold=0 for ambiguous)."""
    aware = local_naive.replace(tzinfo=TZ)
    return aware.utcoffset() == timedelta(hours=-2)


def build(d):
    ts = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
          "order_delivered_customer_date", "order_estimated_delivery_date"]
    o = pd.read_csv(os.path.join(d, "olist_orders_dataset.csv"), parse_dates=ts)
    c = pd.read_csv(os.path.join(d, "olist_customers_dataset.csv"))
    it = pd.read_csv(os.path.join(d, "olist_order_items_dataset.csv"))
    rv = pd.read_csv(os.path.join(d, "olist_order_reviews_dataset.csv"),
                     usecols=["review_id", "order_id", "review_score", "review_answer_timestamp"])
    so, exp, pick = frame(o, c, it)
    n = len(so)
    oidx = {x: i for i, x in enumerate(so.order_id)}

    pt = so.order_purchase_timestamp
    day = ((pt.dt.normalize() - DAY0).dt.days).astype(int).tolist()
    mod = (pt.dt.hour * 60 + pt.dt.minute).astype(int).tolist()
    deliv = [None if pd.isna(dl) else int(math.floor((dl - p).total_seconds() / 86400))
             for dl, p in zip(so.order_delivered_customer_date, pt)]

    li = it[it.order_id.isin(oidx)].copy()
    li["o"] = li.order_id.map(oidx)
    li = li.sort_values(["o", "order_item_id"]).reset_index(drop=True)
    items = [0] * n
    gmv = [0] * n
    fr = [0] * n
    for o_, p, f in zip(li.o, li.price, li.freight_value):
        items[o_] += 1
        gmv[o_] += int(round(p * 100))
        fr[o_] += int(round(f * 100))

    r2 = rv[rv.order_id.isin(oidx)].sort_values(["order_id", "review_answer_timestamp", "review_id"])
    first_score = r2.groupby("order_id").review_score.first()
    review = [int(first_score[x]) if x in first_score.index else None for x in so.order_id]

    # ------------------------------------------------ daylight-saving windows (IANA tz via zoneinfo)
    # A day is "in DST" for the engine when 00:30 civil time that day is in DST. The engine shifts an
    # order to the previous day when it is in such a day and placed before 01:00. Assert that rule
    # equals a direct conversion: civil -> UTC (correct offset) -> civil with a fixed -03:00 offset.
    last_day = max(day)
    in_dst = []
    for k in range(last_day + 1):
        dt = datetime(2016, 9, 1) + timedelta(days=k, minutes=30)
        in_dst.append(dst_at(dt))
    windows, k = [], 0
    while k <= last_day:
        if in_dst[k]:
            s = k
            while k + 1 <= last_day and in_dst[k + 1]:
                k += 1
            windows.append([s, k])
        k += 1
    shifted_direct = 0
    shifted_rule = 0
    for t, dd, mm in zip(pt, day, mod):
        local = t.to_pydatetime()
        aware = local.replace(tzinfo=TZ)
        utc = aware.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
        fixed = utc - timedelta(hours=3)
        if fixed.date() != local.date():
            shifted_direct += 1
        if any(a <= dd <= b for a, b in windows) and mm < 60:
            shifted_rule += 1
    assert shifted_direct == shifted_rule, (shifted_direct, shifted_rule)
    print("DST windows:", windows, "orders shifted by a fixed -03:00 offset:", shifted_direct)

    # ------------------------------------------------ reference totals (independent path, pandas)
    ref = {
        "orders": int(n),
        "lines": int(len(li)),
        "itemValueCents": int(round(li.price.sum() * 100)),
        "freightCents": int(round(li.freight_value.sum() * 100)),
        "reviewed": int(sum(r is not None for r in review)),
        "unreviewed": int(sum(r is None for r in review)),
        "reviewMean": float(np.mean([r for r in review if r is not None])),
        "days": int(len(set(day))),
        "firstDay": str((DAY0 + pd.Timedelta(days=min(day))).date()),
        "lastDay": str((DAY0 + pd.Timedelta(days=max(day))).date()),
        "dstShifted": shifted_direct,
        "multiLineOrders": int(sum(1 for x in items if x > 1)),
        "exportC": int(exp.count(2)),
        "eveningOrders": int(sum(1 for x in mod if x >= 21 * 60)),
    }
    assert abs(sum(gmv) - ref["itemValueCents"]) <= 2, (sum(gmv), ref["itemValueCents"])
    assert abs(sum(fr) - ref["freightCents"]) <= 2, (sum(fr), ref["freightCents"])
    ref["itemValueCents"] = sum(gmv)
    ref["freightCents"] = sum(fr)

    data = {
        "about": ("Derived and masked from the Brazilian E-Commerce Public Dataset by Olist (CC BY-NC-SA 4.0). "
                  "Same 8,614 delivered orders as learn-ship-ecommerce-enabler-with-phoebe and "
                  "learn-ship-social-commerce-with-phoebe. Serai Commerce, its two warehouses, the drifts and the "
                  "parity bar are constructed; no review text."),
        "seed": SEED, "day0": "2016-09-01", "tz": "America/Sao_Paulo",
        "exports": EXPORTS, "nOrders": n,
        "dayDelta": [day[0]] + [day[i] - day[i - 1] for i in range(1, n)],
        "mod": mod, "exp": exp, "items": items, "gmv": gmv, "fr": fr, "review": review, "deliv": deliv,
        "dstWindows": windows,
        "reference": ref,
    }
    return data


def write(data):
    body = json.dumps(data, separators=(",", ":"))
    with open(os.path.join(HERE, "spm-sample.json"), "w") as f:
        f.write(body)
    js = ("/* spm-sample.js - generated by materials/build-spm-data.py with json.dumps. Derived, masked rows from the\n"
          " * Brazilian E-Commerce Public Dataset by Olist (CC BY-NC-SA 4.0). Serai Commerce, its legacy and new\n"
          " * warehouses, the planted drifts and the parity bar are CONSTRUCTED. No review text. */\n"
          "window.SPM_DATA = " + body + ";\n")
    out = os.path.join(HERE, "..", "assets", "spm-sample.js")
    with open(out, "w") as f:
        f.write(js)
    print(f"wrote assets/spm-sample.js ({len(js)} bytes) and materials/spm-sample.json")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    D = build(sys.argv[1])
    print(json.dumps(D["reference"]))
    if "--write" in sys.argv:
        write(D)
