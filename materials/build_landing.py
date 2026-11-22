#!/usr/bin/env python3
"""Write index.html for learn-ship-platform-migration-with-phoebe. Internal build script.

The knowledge-map data is serialised with json.dumps (never string interpolation).
Usage: python3 -I materials/build_landing.py
"""
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
G, Y, O, R = "#34D399", "#FBBF24", "#FB923C", "#F87171"

LEADER = [
    ("a1-why-migrations-break-the-numbers.html", "🧯", "Why migrations break the numbers", G,
     "Seven ways a warehouse move changes a number without an error message, planted on 8,614 real orders, and what done means on cutover day.",
     ["Seven quiet drifts", "Done means explained", "Five rungs of checks"], "▶ Start here"),
    ("a2-inventory-before-plan.html", "📋", "Inventory before plan", Y,
     "What you own, who reads it and what nobody reads. In Serai's constructed estate, 83 of 214 tables went unread for 90 days.",
     ["What you own", "Who reads it", "Retire first"], None),
    ("a3-lift-rebuild-or-retire.html", "🧭", "Sequence and scope: lift, rebuild or retire", Y,
     "One decision per asset, and the order of moves. Big bang against a phased, parallel move, taught as the disagreement it is.",
     ["Lift, rebuild, retire", "Big bang or phased", "The order of moves"], None),
    ("a4-the-parity-bar.html", "⚖️", "The parity bar", O,
     "Which differences you accept, signed before anyone looks. Exact daily checks raise 2 false alarms; a 3% bar on every metric lets a real defect through.",
     ["Accepted differences", "Tolerance by metric", "Too loose a bar"], None),
    ("a5-cutover-day-and-the-rollback.html", "🚦", "Cutover day and the rollback", O,
     "Go/no-go, the freeze, and rollback criteria written while everyone is calm, with two real incidents read closely.",
     ["Go/no-go", "The freeze", "Rollback criteria"], None),
    ("a6-the-week-after-and-switching-off.html", "🔌", "The week after and switching off", R,
     "The drift that hides inside a month, the decommission log, and why the cost case only closes when the old system is off.",
     ["Drift watch", "Decommission log", "Cost case closed"], "the decision"),
]
BUILDER = [
    ("b1-inventory-from-the-query-log.html", "🔎", "Inventory from the query log", G,
     "Usage and lineage from 90 days of a constructed query log in DuckDB: which tables are read, by whom, and which are dead.",
     ["Reads, not tables", "Lineage from SQL", "Dead assets"], "▶ Start here"),
    ("b2-the-dependency-graph.html", "🕸️", "The dependency graph and the order of moves", Y,
     "Turn the inventory into a graph and the graph into an order: leaves first, shared sources last, cycles named.",
     ["The graph", "Topological order", "Waves of moves"], None),
    ("b3-translate-the-sql.html", "🔤", "Translate the SQL", Y,
     "Dialect gaps that compile and still change the answer: time zones, NULL, integer division and collation, each run in DuckDB.",
     ["Dates and time zones", "NULL and empty", "Division and collation"], None),
    ("b4-row-and-key-parity.html", "🔑", "Row and key parity", Y,
     "Counts catch 1 of 5 planted defects. Keys add the 1,767 orders whose customer key no longer resolves.",
     ["Counts", "Keys both ways", "Duplicates"], None),
    ("b5-aggregate-parity.html", "📊", "Aggregate parity at the grain people read", O,
     "Six metrics by day and by month, with tolerances by metric, and why exact equality on floating point is an alarm machine.",
     ["Daily and monthly", "Tolerance by metric", "Float and rounding"], None),
    ("b6-historical-reload.html", "📦", "Historical reload", O,
     "Reloading history as one cutover step, and the 367 late rows that came back twice.",
     ["Reload windows", "Late rows", "Reload, then check"], None),
    ("b7-parallel-run.html", "🛤️", "Parallel run", O,
     "Two systems, one truth: the diff dashboard that runs every night until the numbers stop moving.",
     ["Two systems", "The diff dashboard", "Exit criteria"], None),
    ("b8-cutover-rehearsal-and-rollback.html", "🎬", "Cutover rehearsal and rollback", R,
     "Rehearse the cutover end to end, time it, and test the rollback as hard as the move.",
     ["Rehearse", "Time it", "Roll back for real"], None),
    ("b9-drift-that-hides.html", "🕳️", "The week after: drift that hides", R,
     "72 orders move a day in Brazilian summer time: 74 daily numbers change and no monthly number does.",
     ["Time-zone edges", "Late data", "Caches"], None),
    ("b10-the-parity-bench.html", "🎛️", "The parity bench", R,
     "Seven planted drifts on 8,614 real orders, five rungs of checks, a loose bar and a break button. Capstone: Serai's signed runbook.",
     ["Five rungs", "The loose bar", "Both sides on new"], "the capstone"),
]
SHORT = {
    "a1": "Why numbers break", "a2": "Inventory", "a3": "Lift or retire", "a4": "Parity bar", "a5": "Cutover day",
    "a6": "Week after", "b1": "Query log", "b2": "Dependency graph", "b3": "Translate SQL", "b4": "Row and key",
    "b5": "Aggregates", "b6": "Reload", "b7": "Parallel run", "b8": "Rehearsal", "b9": "Hidden drift",
    "b10": "Parity bench",
}


def cards(rows, track):
    out = []
    for i, (f, icon, title, diff, blurb, _c, pill) in enumerate(rows):
        n = i + 1
        cnum = f"{track} session {n}" + (" · start here" if n == 1 else "")
        meta = f'\n        <span class="meta"><span class="pill amber">{html.escape(pill)}</span></span>' if pill else ""
        out.append(f'''      <a class="course-card" href="courses/{f}" style="--diff:{diff}">
        <span class="cicon">{icon}</span>
        <span class="cnum">{cnum}</span>
        <h3>{html.escape(title)}</h3>
        <p>{html.escape(blurb)}</p>{meta}
      </a>''')
    return "\n".join(out)


def mindmap():
    sessions = []
    for rows in (LEADER, BUILDER):
        for f, _i, _t, diff, _b, concepts, _p in rows:
            key = f.split("-")[0]
            sessions.append({"label": SHORT[key], "href": "courses/" + f, "color": diff,
                             "concepts": [{"label": c, "href": "courses/" + f} for c in concepts]})
    return {"title": "Data Platform\nMigration", "centerColor": "#46330F", "sessions": sessions}


def path(label, steps, note):
    parts = []
    for i, (code, f) in enumerate(steps):
        if i:
            parts.append('        <span class="parr">→</span>')
        parts.append(f'        <a class="pstep" href="courses/{f}">{code}</a>')
    return (f'      <div class="path"><b>{label}</b>\n' + "\n".join(parts) +
            f'\n        <span style="font-size:.82rem;color:var(--muted)">{note}</span>\n      </div>')


def main():
    donor_style = open(os.path.join(HERE, "landing-style.css")).read()
    L = {r[0][:2]: r[0] for r in LEADER}
    B = {r[0].split("-")[0]: r[0] for r in BUILDER}
    paths = "\n".join([
        path("💼 I approve the move", [("L1", L["a1"]), ("L3", L["a3"]), ("L4", L["a4"]), ("L5", L["a5"]), ("L6", L["a6"])],
             "failure modes, scope, the bar, cutover, switching off"),
        path("🗂️ I map the estate", [("B1", B["b1"]), ("B2", B["b2"]), ("L2", L["a2"]), ("B3", B["b3"])],
             "query log, graph, inventory, translation"),
        path("🧪 I prove the numbers", [("B4", B["b4"]), ("B5", B["b5"]), ("B7", B["b7"]), ("B9", B["b9"]), ("B10", B["b10"])],
             "keys, aggregates, parallel run, hidden drift, then the bench"),
    ])
    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- social:start -->
<meta name="description" content="Sixteen sessions on moving a data warehouse without breaking the numbers: inventory, scope, SQL translation, parity tests, historical reload, parallel run, cutover with a rehearsed rollback and the week after, on 8,614 real Olist orders under a constructed company, with a parity bench computed in your browser. Free, by Phoebe Fu.">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Learn with Phoebe">
<meta property="og:title" content="Learn Ship It: Data Platform Migration with Phoebe">
<meta property="og:description" content="Move a warehouse without breaking the numbers. Inventory, parity on real orders, a rehearsed rollback and the drift that shows up the week after.">
<meta property="og:url" content="https://phoebefu6.github.io/learn-ship-platform-migration-with-phoebe/">
<meta property="og:image" content="https://phoebefu6.github.io/learn-ship-platform-migration-with-phoebe/assets/og-cover.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Learn Ship It: Data Platform Migration with Phoebe">
<meta name="twitter:description" content="Row counts catch 1 of 5 planted defects. The full parity suite catches 5 with no false alarm.">
<meta name="twitter:image" content="https://phoebefu6.github.io/learn-ship-platform-migration-with-phoebe/assets/og-cover.png">
<!-- social:end -->
<title>Learn Ship It: Data Platform Migration with Phoebe</title>
<link rel="stylesheet" href="assets/style.css?v=1">
<style>
{donor_style}</style>
</head>
<body>

<header class="masthead">
  <div class="wrap">
    <div class="eyebrow">Learn with Phoebe · Let's Ship It End to End</div>
    <h1>Ship It: <span class="accent">Data Platform Migration</span></h1>
    <p class="sub">Move a warehouse without breaking the numbers. Serai Commerce, a constructed Southeast Asian commerce enabler, is moving its warehouse from a legacy stack to a new one; underneath are the same 8,614 real orders from the public Olist dataset its sibling courses use. Six leader sessions decide what to move, in what order, which differences to accept, when to cut over and when to switch the old system off. Ten builder sessions do the move: inventory from the query log, the dependency graph, SQL translation, row, key and aggregate parity, historical reload, a parallel run, a rehearsed rollback, the drift that hides the week after, and a parity bench computed in your browser. On cutover day, can you prove every number the business reads is the same, or say exactly why it changed?</p>
    <div class="stats-row">
      <div class="stat"><b data-count="16">16</b><span>sessions, two tracks</span></div>
      <div class="stat"><b data-count="8614">8,614</b><span>real orders</span></div>
      <div class="stat"><b data-count="7">7</b><span>planted drifts</span></div>
      <div class="stat"><b data-count="5">5</b><span>rungs of checks</span></div>
      <div class="stat"><b data-count="45">45</b><span>min per session</span></div>
    </div>
  </div>
</header>

<main class="wrap">

  <section class="section">
    <div class="paths" style="margin-top:0">
      <h2>Leader track 🧭 <span style="font-size:.85rem;font-weight:600;color:var(--muted)">· six sessions, no code</span></h2>
      <p class="plede">For heads of data and platform owners asked to approve or run a warehouse move. Decide the scope, the order, the bar the numbers must clear, the cutover call and the day the old system goes dark.</p>
    </div>

    <div class="course-grid">
{cards(LEADER, "Leader")}
    </div>
  </section>

  <section class="section">
    <div class="paths" style="margin-top:0">
      <h2>Builder track 🔧 <span style="font-size:.85rem;font-weight:600;color:var(--muted)">· ten sessions, SQL in DuckDB and the browser</span></h2>
      <p class="plede">The move itself, in the order a careful team does it: find out what is used, order the moves, translate, prove parity three ways, reload, run in parallel, rehearse, cut over and watch.</p>
    </div>

    <div class="course-grid">
{cards(BUILDER, "Builder")}
    </div>

    <div class="diff-legend">
      <span><i style="background:#34D399"></i>start here</span>
      <span><i style="background:#FBBF24"></i>foundations</span>
      <span><i style="background:#FB923C"></i>hands-on</span>
      <span><i style="background:#F87171"></i>capstone</span>
    </div>
  </section>

  <section class="section">
    <div class="paths">
      <h2>Choose your path 🗺️</h2>
      <p class="plede">Three doors into the same move. Each starts at the part its reader is answerable for.</p>
{paths}
    </div>
  </section>

  <section class="section">
    <div class="paths" style="margin-top:0">
      <h2>Your passport 🎫</h2>
      <p class="plede">Clear all three quiz questions in a session and it gets stamped. Sixteen stamps across both tracks, and they live in this browser only.</p>
    </div>
    <div class="pp-strip"></div>
  </section>

  <section class="section">
    <div class="paths" style="margin-top:0">
      <h2>What is real here 🧾</h2>
      <p class="plede">A course about trustworthy numbers should be exact about which of its own are measured.</p>
    </div>
    <table class="clean">
      <tr><th>Claim</th><th>Status</th></tr>
      <tr><td>Serai Commerce, its two warehouses, its inventory counts and its parity bar</td><td>Constructed, continued from the Social Commerce courses and labelled wherever it appears. No real company's data is shown</td></tr>
      <tr><td>The orders, items, prices, freight, purchase times and review scores</td><td>Real: 8,614 delivered orders from the Brazilian E-Commerce Public Dataset by Olist (CC BY-NC-SA 4.0), derived and masked; the same sample the sibling Ship It courses use. No review text is used</td></tr>
      <tr><td>The seven drifts in the new warehouse</td><td>Constructed rules applied to real rows. The orders each one touches are real, for example the 72 placed just after midnight in Brazilian summer time</td></tr>
      <tr><td>Every count, key diff, aggregate and verdict on the bench</td><td>Computed live in your browser on those rows. An independent Python reference matches all 1,740 numbers on the ladder</td></tr>
      <tr><td>SQL behaviour: integer division, NULL, time zones, collation</td><td>Read at source in the PostgreSQL, DuckDB, Oracle and MySQL documentation, and run in DuckDB in the builder track</td></tr>
      <tr><td>Two real incidents: a bank's 2018 platform migration and a 2018 database failover</td><td>Read at source in the regulator's notice, the bank's own release and the company's post-incident analysis. Findings of the bank's independent review are marked reported</td></tr>
      <tr><td>Big bang against a phased move, and how long a parallel run should last</td><td>Contested, and taught as a disagreement. No source gives a number; Serai's four-week parallel run is constructed</td></tr>
    </table>
  </section>

  <section class="section mm-section">
    <h2>The knowledge map 🧠</h2>
    <p class="mm-lede">Both tracks at a glance - hover a session to spotlight its concepts, click any node to jump in.</p>
    <div class="mm-wrap"><div id="mindmap"></div></div>
  </section>

  <footer class="pagefoot">
    <span>learn-ship-platform-migration-with-phoebe · by Phoebe Fu &nbsp;·&nbsp; 📚 <a href="https://phoebefu6.github.io/learn-with-phoebe/">Learn with Phoebe ↗</a></span>
    <span>Pairs with <a href="https://phoebefu6.github.io/learn-ship-social-commerce-with-phoebe/">Ship It: Social Commerce ↗</a> and <a href="https://phoebefu6.github.io/learn-dataops-with-phoebe/">DataOps ↗</a></span>
  </footer>

</main>

<script>
window.MINDMAP_DATA = {json.dumps(mindmap(), indent=2, ensure_ascii=False)};
</script>
<script src="assets/mindmap.js?v=1"></script>
<script src="assets/app.js?v=1"></script>
</body>
</html>
'''
    with open(os.path.join(HERE, "..", "index.html"), "w") as f:
        f.write(page)
    print("wrote index.html")


if __name__ == "__main__":
    main()
