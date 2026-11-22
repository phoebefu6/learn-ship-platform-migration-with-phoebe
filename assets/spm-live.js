/* spm-live.js - the parity bench for learn-ship-platform-migration-with-phoebe
 *
 * Serai Commerce is CONSTRUCTED. The rows are REAL but derived and masked: the same 8,614 delivered
 * Olist orders as learn-ship-ecommerce-enabler-with-phoebe and learn-ship-social-commerce-with-phoebe
 * (Brazilian E-Commerce Public Dataset by Olist, CC BY-NC-SA 4.0), built by
 * materials/build-spm-data.py into assets/spm-sample.js.
 *
 * The legacy warehouse holds one row per order, as the source has it. The new warehouse is the same
 * rows after a migration that carries CONSTRUCTED drifts, each a deterministic rule on the real rows:
 *   late   defect   orders delivered more than 30 days after purchase arrive again on the late-row
 *                   feed and are appended instead of merged (a second row, same key)
 *   tz     defect   the new reporting layer turns UTC back into local time with a fixed -03:00 offset,
 *                   which ignores Brazilian daylight saving: orders placed 00:00 to 00:59 in summer
 *                   time land on the previous day
 *   nul    defect   a missing review score is exported as an empty string and loaded as 0
 *   idiv   defect   items per order is computed as integer / integer, which truncates in the new dialect
 *   case   defect   Export C writes customer keys in lower case; the new engine compares keys
 *                   case-sensitively, so those orders lose their customer
 *   round  accepted order freight is split equally across lines and rounded per line
 *   float  accepted money is summed as floating point instead of integer cents
 * The parity suite, COMPUTED LIVE on every click, compares the two warehouses:
 *   counts  total rows                     keys   primary keys missing, extra, duplicated; customer keys resolving
 *   daily   six metrics per day, exact     parity six metrics per month, each within its signed tolerance
 *   edge    for orders placed within an hour of local midnight, the day each warehouse assigns
 * Each drift is planted ALONE and the suite is scored: a defect that raises an alarm is caught, a
 * defect that raises none is missed, an accepted difference (or no drift at all) that raises an alarm
 * is a false alarm.
 * Anti-lever: the loose bar (3% on every metric). Break button: point both sides at the new warehouse.
 *
 * materials/spm_reference.py is an independent pure-Python reference; materials/compare-ladder.py
 * checks that it and this file print the same canon over the whole ladder.
 */
(function (root) {
  "use strict";

  var LATE_DAYS = 30;
  var EDGE_MIN = 60;
  var METRICS = ["orders", "itemValue", "freight", "itemsPerOrder", "reviewed", "avgReview"];
  var METRIC_LABEL = { orders: "Orders", itemValue: "Item value (BRL)", freight: "Freight (BRL)",
    itemsPerOrder: "Items per order", reviewed: "Reviewed orders", avgReview: "Average review score" };
  /* Serai's parity bar, CONSTRUCTED policy: monthly grain, signed before cutover. */
  var BAR = {
    orders: { kind: "abs", tol: 0 }, itemValue: { kind: "rel", tol: 0.0005 }, freight: { kind: "rel", tol: 0.0005 },
    itemsPerOrder: { kind: "abs", tol: 0.005 }, reviewed: { kind: "abs", tol: 0 }, avgReview: { kind: "abs", tol: 0.01 }
  };
  var LOOSE = {};
  METRICS.forEach(function (m) { LOOSE[m] = { kind: "rel", tol: 0.03 }; });

  var DRIFTS = [
    { id: "late", kind: "defect", label: "Late rows appended twice" },
    { id: "tz", kind: "defect", label: "Fixed -03:00 offset ignores daylight saving" },
    { id: "nul", kind: "defect", label: "Missing review score loaded as 0" },
    { id: "idiv", kind: "defect", label: "Items per order by integer division" },
    { id: "case", kind: "defect", label: "Case-sensitive customer-key join" },
    { id: "round", kind: "accepted", label: "Freight split per line, rounded per line" },
    { id: "float", kind: "accepted", label: "Money summed as floating point" }
  ];
  var RUNGS = [
    { id: 0, label: "0 · Row counts", checks: ["counts"] },
    { id: 1, label: "1 · + Keys", checks: ["counts", "keys"] },
    { id: 2, label: "2 · + Daily aggregates", checks: ["counts", "keys", "daily"] },
    { id: 3, label: "3 · + Tolerances by metric", checks: ["counts", "keys", "parity"] },
    { id: 4, label: "4 · + Time-zone edge check", checks: ["counts", "keys", "parity", "edge"] }
  ];

  /* ---------- the two warehouses ---------- */
  function prep(D) {
    if (D._day) return D;
    var dd = 0;
    D._day = D.dayDelta.map(function (x) { dd += x; return dd; });
    return D;
  }

  function inDst(D, day) {
    for (var i = 0; i < D.dstWindows.length; i++) if (day >= D.dstWindows[i][0] && day <= D.dstWindows[i][1]) return true;
    return false;
  }

  function legacy(D) {
    prep(D);
    var rows = [];
    for (var k = 0; k < D.nOrders; k++) {
      rows.push({ k: k, day: D._day[k], mod: D.mod[k], exp: D.exp[k], items: D.items[k], gmv: D.gmv[k], fr: D.fr[k], rev: D.review[k], fk: 1 });
    }
    return { rows: rows, idiv: false, float: false };
  }

  function copyRow(r) { return { k: r.k, day: r.day, mod: r.mod, exp: r.exp, items: r.items, gmv: r.gmv, fr: r.fr, rev: r.rev, fk: r.fk }; }

  /* drift: one id, "all", or "none". plant: drop the last row (a lossy loader) for the self-test. */
  function newWarehouse(D, drift, plant) {
    prep(D);
    var on = function (id) { return drift === id || drift === "all"; };
    var base = legacy(D).rows.map(copyRow);
    base.forEach(function (r) {
      if (on("tz") && inDst(D, r.day) && r.mod < 60) r.day = r.day - 1;
      if (on("nul") && r.rev === null) r.rev = 0;
      if (on("case") && r.exp === 2) r.fk = 0;
      if (on("round") && r.items > 1) r.fr = r.items * Math.floor((2 * r.fr + r.items) / (2 * r.items));
    });
    var rows = base;
    if (on("late")) {
      var extra = [];
      base.forEach(function (r) { var d = D.deliv[r.k]; if (d !== null && d > LATE_DAYS) extra.push(copyRow(r)); });
      rows = base.concat(extra);
    }
    if (plant) rows = rows.slice(0, rows.length - 1);
    return { rows: rows, idiv: on("idiv"), float: on("float") };
  }

  /* ---------- aggregates ---------- */
  function monthOf(day) {
    var t = new Date(Date.UTC(2016, 8, 1) + day * 86400000);
    var m = t.getUTCMonth() + 1;
    return t.getUTCFullYear() + "-" + (m < 10 ? "0" : "") + m;
  }

  function aggregate(W, grain) {
    var B = {};
    W.rows.forEach(function (r) {
      var key = grain === "day" ? String(r.day) : monthOf(r.day);
      var b = B[key];
      if (!b) b = B[key] = { n: 0, items: 0, gmvC: 0, frC: 0, gmvF: 0, frF: 0, revN: 0, revS: 0 };
      b.n += 1; b.items += r.items; b.gmvC += r.gmv; b.frC += r.fr;
      b.gmvF += r.gmv / 100; b.frF += r.fr / 100;
      if (r.rev !== null) { b.revN += 1; b.revS += r.rev; }
    });
    var out = {};
    Object.keys(B).forEach(function (key) { out[key] = metricsOf(B[key], W); });
    return out;
  }

  function metricsOf(b, W) {
    return {
      orders: b.n,
      itemValue: W.float ? b.gmvF : b.gmvC / 100,
      freight: W.float ? b.frF : b.frC / 100,
      itemsPerOrder: b.n ? (W.idiv ? Math.floor(b.items / b.n) : b.items / b.n) : null,
      reviewed: b.revN,
      avgReview: b.revN ? b.revS / b.revN : null
    };
  }

  var EMPTY = { orders: 0, itemValue: 0, freight: 0, itemsPerOrder: null, reviewed: 0, avgReview: null };

  function sortedKeys(a, b, grain) {
    var s = {};
    Object.keys(a).forEach(function (k) { s[k] = 1; });
    Object.keys(b).forEach(function (k) { s[k] = 1; });
    var ks = Object.keys(s);
    if (grain === "day") ks.sort(function (x, y) { return Number(x) - Number(y); });
    else ks.sort();
    return ks;
  }

  function differs(a, b, rule) {
    if (a === null && b === null) return false;
    if (a === null || b === null) return true;
    if (!rule) return a !== b;
    var d = Math.abs(a - b);
    if (rule.kind === "abs") return d > rule.tol;
    return d > rule.tol * Math.abs(a);
  }

  /* per metric: buckets compared, buckets failing, largest absolute gap */
  function compareAgg(LA, NA, grain, bar) {
    var ks = sortedKeys(LA, NA, grain), out = {};
    METRICS.forEach(function (m) { out[m] = { fail: 0, maxGap: 0 }; });
    ks.forEach(function (k) {
      var a = LA[k] || EMPTY, b = NA[k] || EMPTY;
      METRICS.forEach(function (m) {
        var x = a[m], y = b[m];
        if (differs(x, y, bar ? bar[m] : null)) out[m].fail += 1;
        if (x !== null && y !== null) out[m].maxGap = Math.max(out[m].maxGap, Math.abs(x - y));
      });
    });
    var failing = 0;
    METRICS.forEach(function (m) { failing += out[m].fail; });
    return { buckets: ks.length, metrics: out, failing: failing };
  }

  /* ---------- the five checks ---------- */
  function checkCounts(L, N) {
    return { legacy: L.rows.length, fresh: N.rows.length, alarm: L.rows.length !== N.rows.length };
  }

  /* Two-sided: each side's key counts and unresolved customer keys, then compared. */
  function keySide(W, n) {
    var cnt = new Array(n).fill(0), fk = 0;
    W.rows.forEach(function (r) {
      if (cnt[r.k] === 0 && !r.fk) fk += 1;
      cnt[r.k] += 1;
    });
    var dup = 0;
    for (var k = 0; k < n; k++) if (cnt[k] > 1) dup += 1;
    return { cnt: cnt, dup: dup, fk: fk };
  }

  function checkKeys(L, N, n) {
    var a = keySide(L, n), b = keySide(N, n), missing = 0, extra = 0;
    for (var k = 0; k < n; k++) {
      if (a.cnt[k] > 0 && b.cnt[k] === 0) missing += 1;
      if (b.cnt[k] > 0 && a.cnt[k] === 0) extra += 1;
    }
    return { missing: missing, extra: extra, dupLegacy: a.dup, duplicated: b.dup, unresolvedLegacy: a.fk, unresolvedNew: b.fk,
      alarm: missing > 0 || extra > 0 || a.dup !== b.dup || a.fk !== b.fk };
  }

  function checkEdge(D, L, N) {
    var first = {}, near = 0, mism = 0;
    N.rows.forEach(function (r) { if (first[r.k] === undefined) first[r.k] = r.day; });
    L.rows.forEach(function (r) {
      if (r.mod < EDGE_MIN || r.mod >= 1440 - EDGE_MIN) {
        near += 1;
        if (first[r.k] !== undefined && first[r.k] !== r.day) mism += 1;
      }
    });
    return { near: near, mismatched: mism, alarm: mism > 0 };
  }

  function totals(W) {
    var all = aggregate({ rows: W.rows.map(function (r) { var c = copyRow(r); c.day = 0; return c; }), idiv: W.idiv, float: W.float }, "month");
    return all[Object.keys(all)[0]];
  }

  /* Every check on one (legacy, new) pair; the rung decides which checks count. */
  function detail(D, L, N, loose) {
    var Ld = aggregate(L, "day"), Nd = aggregate(N, "day"), Lm = aggregate(L, "month"), Nm = aggregate(N, "month");
    var daily = compareAgg(Ld, Nd, "day", null);
    var parity = compareAgg(Lm, Nm, "month", loose ? LOOSE : BAR);
    daily.alarm = daily.failing > 0;
    parity.alarm = parity.failing > 0;
    return { counts: checkCounts(L, N), keys: checkKeys(L, N, D.nOrders), daily: daily, parity: parity,
      edge: checkEdge(D, L, N), totals: { legacy: totals(L), fresh: totals(N) } };
  }

  function touched(D, id) {
    prep(D);
    var c = 0;
    for (var k = 0; k < D.nOrders; k++) {
      var it = D.items[k];
      if (id === "late" && D.deliv[k] !== null && D.deliv[k] > LATE_DAYS) c++;
      else if (id === "tz" && inDst(D, D._day[k]) && D.mod[k] < 60) c++;
      else if (id === "nul" && D.review[k] === null) c++;
      else if (id === "case" && D.exp[k] === 2) c++;
      else if (id === "round" && it > 1 && it * Math.floor((2 * D.fr[k] + it) / (2 * it)) !== D.fr[k]) c++;
      else if (id === "idiv" || id === "float") c++;
    }
    return c;
  }

  function score(D, dets, rung) {
    var checks = RUNGS[rung].checks, out = { caught: 0, missed: 0, falseAlarms: 0, quiet: 0, verdicts: {} };
    ["none"].concat(DRIFTS.map(function (d) { return d.id; })).forEach(function (id) {
      var det = dets[id], fired = checks.filter(function (c) { return det[c].alarm; });
      var kind = id === "none" ? "control" : DRIFTS.filter(function (d) { return d.id === id; })[0].kind;
      var v;
      if (kind === "defect") { v = fired.length ? "caught" : "missed"; if (fired.length) out.caught++; else out.missed++; }
      else { v = fired.length ? "false alarm" : "quiet"; if (fired.length) out.falseAlarms++; else out.quiet++; }
      out.verdicts[id] = { verdict: v, fired: fired };
    });
    return out;
  }

  /* Everything for one mode. mode: "normal" | "loose" | "break" */
  function run(D, mode, plant) {
    prep(D);
    var L = legacy(D), dets = {};
    ["none"].concat(DRIFTS.map(function (d) { return d.id; })).forEach(function (id) {
      var N = newWarehouse(D, id, plant && id === "none");
      dets[id] = mode === "break" ? detail(D, N, N, false) : detail(D, L, N, mode === "loose");
    });
    var NA = newWarehouse(D, "all", false);
    var all = mode === "break" ? detail(D, NA, NA, false) : detail(D, L, NA, mode === "loose");
    var rungs = RUNGS.map(function (r) { return score(D, dets, r.id); });
    return { mode: mode, perDrift: dets, all: all, rungs: rungs };
  }

  function ladder(D) {
    prep(D);
    var t = {};
    DRIFTS.forEach(function (d) { t[d.id] = touched(D, d.id); });
    return { normal: run(D, "normal"), loose: run(D, "loose"), brk: run(D, "break"), touched: t,
      reference: D.reference, lateDays: LATE_DAYS };
  }

  /* Properties that must hold on the shipped data; selfTest(D, true) plants a lossy loader (the last
   * row of the new warehouse dropped) into the no-drift control, so at least two properties must fail. */
  function selfTest(D, plant) {
    var N = run(D, "normal", plant), Lo = run(D, "loose", plant), B = run(D, "break", plant), T = totals(legacy(D));
    var ref = D.reference, props = [], top = N.rungs[4];
    function p(name, ok) { props.push({ name: name, ok: !!ok }); }
    p("legacy totals reproduce the builder's reference (orders, cents, reviews)",
      T.orders === ref.orders && Math.round(T.itemValue * 100) === ref.itemValueCents && Math.round(T.freight * 100) === ref.freightCents && T.reviewed === ref.reviewed);
    p("the no-drift control raises no alarm on any check",
      ["counts", "keys", "daily", "parity", "edge"].every(function (c) { return !N.perDrift.none[c].alarm; }));
    p("the daylight-saving drift moves exactly the orders the builder counted with zoneinfo", touched(D, "tz") === ref.dstShifted);
    p("the full suite catches every defect with no false alarm", top.caught === 5 && top.falseAlarms === 0);
    p("exact daily comparison flags both accepted differences", N.rungs[2].falseAlarms === 2);
    p("the loose bar catches fewer defects than the signed bar", Lo.rungs[4].caught < top.caught);
    p("pointing both sides at the new warehouse catches nothing", B.rungs[4].caught === 0);
    p("the late-row drift adds exactly one row per late order", N.perDrift.late.counts.fresh - N.perDrift.late.counts.legacy === touched(D, "late"));
    var held = props.filter(function (x) { return x.ok; }).length;
    return { pass: held === props.length, held: held, total: props.length,
      failed: props.filter(function (x) { return !x.ok; }).map(function (x) { return x.name; }) };
  }

  /* ---------- UI ---------- */
  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function fmt(n) { return Number(n).toLocaleString("en-US"); }
  function brl(x) { return "BRL " + Number(x).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function val(m, x) {
    if (x === null || x === undefined) return "none";
    if (m === "itemValue" || m === "freight") return brl(x);
    if (m === "itemsPerOrder" || m === "avgReview") return x.toFixed(4);
    return fmt(x);
  }
  function kind(k) { return '<span class="spm-kind is-' + k + '">' + k + "</span>"; }
  function metric(label, value, unit, k) {
    return '<div class="spm-metric"><span class="spm-mlabel">' + esc(label) + '</span><span class="spm-mvalue">' + value +
      '</span><span class="spm-munit">' + esc(unit) + "</span>" + kind(k) + "</div>";
  }
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html !== undefined) e.innerHTML = html; return e; }
  function block(title, inner) { return '<div class="spm-block"><h5 class="spm-bh">' + title + "</h5>" + inner + "</div>"; }
  function barText(rule) { return rule.kind === "rel" ? "within " + (rule.tol * 100).toFixed(2) + "%" : (rule.tol === 0 ? "exact" : "within " + rule.tol); }

  var D, ui = {}, state = { rung: 0, loose: false, brk: false }, cache = {}, T = {};

  function current() {
    var mode = state.brk ? "break" : state.loose ? "loose" : "normal";
    if (!cache[mode]) cache[mode] = run(D, mode);
    return cache[mode];
  }

  function checkText(id, c, det) {
    if (c === "counts") return det.counts.alarm ? "rows " + fmt(det.counts.legacy) + " vs " + fmt(det.counts.fresh) : "rows equal";
    if (c === "keys") {
      var k = det.keys;
      return k.alarm ? [k.duplicated ? fmt(k.duplicated) + " duplicated keys" : "", k.missing ? fmt(k.missing) + " missing" : "",
        k.unresolvedNew !== k.unresolvedLegacy ? fmt(k.unresolvedNew) + " customer keys unresolved" : ""].filter(Boolean).join(", ") : "keys match";
    }
    var a = c === "daily" ? det.daily : det.parity;
    if (c === "daily" || c === "parity") {
      if (!a.alarm) return (c === "daily" ? "all " + fmt(a.buckets) + " days equal" : "every month inside the bar");
      return METRICS.filter(function (m) { return a.metrics[m].fail; }).map(function (m) {
        return METRIC_LABEL[m] + " " + fmt(a.metrics[m].fail) + (c === "daily" ? " days" : " months");
      }).join(", ");
    }
    return det.edge.alarm ? fmt(det.edge.mismatched) + " of " + fmt(det.edge.near) + " near-midnight orders on another day" : fmt(det.edge.near) + " near-midnight orders, same day";
  }

  function render() {
    var R = current(), S = R.rungs[state.rung], checks = RUNGS[state.rung].checks, html = "";
    ui.rbtn.forEach(function (b, i) { b.classList.toggle("is-on", i === state.rung); });
    ui.looseBtn.classList.toggle("is-on", state.loose);
    ui.looseBtn.textContent = state.loose ? "Loose bar on: restore the signed bar" : "Loosen the bar: 3% on every metric";
    ui.brkBtn.classList.toggle("is-on", state.brk);
    ui.brkBtn.textContent = state.brk ? "Both sides read the new warehouse: point legacy back at legacy" : "Break it: point both sides of the comparison at the new warehouse";

    html += '<div class="spm-metrics">' +
      metric("Defects caught", S.caught + " of 5", "planted one at a time; each needs at least one alarm", "measured") +
      metric("Defects missed", String(S.missed), "a missed defect reaches the business on cutover day", "measured") +
      metric("False alarms", S.falseAlarms + " of 3", "two accepted differences plus a no-drift control", "measured") +
      "</div>";

    var rows = DRIFTS.map(function (d) {
      var v = S.verdicts[d.id], det = R.perDrift[d.id];
      var cls = v.verdict === "caught" || v.verdict === "quiet" ? "is-good" : "is-bad";
      var fired = v.fired.length ? v.fired.map(function (c) { return c + ": " + checkText(d.id, c, det); }).join("; ") : "no check fired";
      return "<tr><td><strong>" + esc(d.label) + "</strong></td><td>" + (d.kind === "defect" ? "defect" : "accepted difference") + "</td><td>" + fmt(T[d.id]) +
        '</td><td><span class="spm-tag ' + cls + '">' + v.verdict + "</span></td><td>" + esc(fired) + "</td></tr>";
    }).join("");
    var c0 = S.verdicts.none;
    rows += "<tr><td><strong>No drift (control)</strong></td><td>control</td><td>0</td><td><span class=\"spm-tag " + (c0.fired.length ? "is-bad" : "is-good") + "\">" + c0.verdict +
      "</span></td><td>" + (c0.fired.length ? esc(c0.fired.join(", ")) : "no check fired") + "</td></tr>";
    html += block("Rung " + state.rung + " · each drift planted alone, checks on: " + checks.join(", "),
      '<div class="spm-tablewrap"><table class="clean spm-table"><thead><tr><th>Drift in the new warehouse</th><th>Kind</th><th>Orders touched</th><th>Verdict</th><th>What fired</th></tr></thead><tbody>' +
      rows + "</tbody></table></div>" +
      '<p class="spm-note">' + kind("constructed") + " Every drift is a constructed rule applied to real rows; the orders it touches are real. " +
      "Items per order and floating-point money change how every order is summed, so they touch all " + fmt(D.nOrders) + ".</p>");

    var A = R.all, tl = A.totals.legacy, tn = A.totals.fresh;
    var trow = METRICS.map(function (m) { return "<tr><td>" + METRIC_LABEL[m] + "</td><td>" + val(m, tl[m]) + "</td><td>" + val(m, tn[m]) + "</td></tr>"; }).join("");
    html += block("Every drift at once · what the board would read",
      '<div class="spm-tablewrap"><table class="clean spm-table"><thead><tr><th>Whole sample</th><th>Legacy</th><th>New</th></tr></thead><tbody>' + trow + "</tbody></table></div>" +
      '<p class="spm-note">Checks with all seven drifts on: ' + ["counts", "keys", "daily", "parity", "edge"].map(function (c) {
        return "<strong>" + c + "</strong> " + (A[c].alarm ? "alarm" : "quiet");
      }).join(" · ") + ".</p>");

    var bar = state.loose ? LOOSE : BAR;
    html += block("The parity bar in force (rungs 3 and 4, monthly grain)",
      '<div class="spm-tablewrap"><table class="clean spm-table"><thead><tr><th>Metric</th><th>Tolerance</th></tr></thead><tbody>' +
      METRICS.map(function (m) { return "<tr><td>" + METRIC_LABEL[m] + "</td><td>" + barText(bar[m]) + "</td></tr>"; }).join("") +
      "</tbody></table></div>" + '<p class="spm-note">' + kind("constructed") + " Serai's own signed policy, not a standard. Rung 2 compares every day exactly instead.</p>");
    ui.body.innerHTML = html;

    var v;
    if (state.brk) v = '<div class="spm-verdict is-bad"><strong>Both sides read the new warehouse.</strong> Every check agrees with itself: ' + S.caught + " of 5 defects caught. A clean parity report proves nothing until you know what each side read.</div>";
    else if (state.loose && state.rung >= 3) v = '<div class="spm-verdict is-bad"><strong>Loose bar.</strong> ' + S.caught + " of 5 defects caught against " + cache.normal.rungs[state.rung].caught + " with the signed bar: a tolerance wide enough to stop every alarm also stops the ones you needed.</div>";
    else if (state.rung === 4 && S.caught === 5 && S.falseAlarms === 0) v = '<div class="spm-verdict is-good"><strong>The full suite.</strong> 5 of 5 defects caught, 0 false alarms. This is the bar to sign before cutover.</div>';
    else v = '<div class="spm-verdict is-ok"><strong>Rung ' + state.rung + " of 4.</strong> " + ["Counts see only drifts that add or drop rows.", "Keys add what a count cannot see: the same number of rows, attached to the wrong things.", "Exact daily aggregates see everything, including differences you already agreed to accept.", "The signed bar silences the accepted differences, and with them a drift that hides inside a month.", ""][state.rung] + "</div>";
    if (state.loose && state.rung < 3) v += '<p class="spm-note">The loose bar changes rungs 3 and 4 only; rungs 0 to 2 use no tolerance.</p>';
    ui.verdict.innerHTML = v;
  }

  function init() {
    var host = document.getElementById("spm-bench");
    if (!host || !root.SPM_DATA) return;
    D = root.SPM_DATA; prep(D);
    DRIFTS.forEach(function (d) { T[d.id] = touched(D, d.id); });
    cache.normal = run(D, "normal");
    var p = el("div", "spm-panel");
    p.appendChild(el("h4", null, "The parity bench · Serai Commerce (constructed) on " + fmt(D.nOrders) + " real orders"));
    p.appendChild(el("p", "spm-intro", "Two warehouses hold the same " + fmt(D.nOrders) + " delivered orders, derived and masked from the public Olist dataset. The new one carries seven constructed drifts, planted one at a time. Pick the checks; the suite runs in your browser on every click and scores what it catches, what it misses and what it cries wolf about."));
    var rr = el("div", "spm-row"); rr.appendChild(el("span", "spm-rlabel", "Rung"));
    ui.rbtn = RUNGS.map(function (r) {
      var b = el("button", "spm-chip", esc(r.label)); b.type = "button";
      b.addEventListener("click", function () { state.rung = r.id; render(); });
      rr.appendChild(b); return b;
    });
    p.appendChild(rr);
    var ar = el("div", "spm-row"); ar.appendChild(el("span", "spm-rlabel", "Anti-lever"));
    ui.looseBtn = el("button", "spm-chip is-anti"); ui.looseBtn.type = "button";
    ui.looseBtn.addEventListener("click", function () { state.loose = !state.loose; render(); });
    ar.appendChild(ui.looseBtn); p.appendChild(ar);
    ui.brkBtn = el("button", "spm-break"); ui.brkBtn.type = "button";
    ui.brkBtn.addEventListener("click", function () { state.brk = !state.brk; render(); });
    p.appendChild(ui.brkBtn);
    ui.verdict = el("div"); p.appendChild(ui.verdict);
    ui.body = el("div", "spm-body"); p.appendChild(ui.body);
    var st = selfTest(D), sp = selfTest(D, true);
    p.appendChild(el("p", "spm-hint", "Self-test on load: " + st.held + " of " + st.total + " properties hold" + (st.failed.length ? " (failing: " + esc(st.failed.join("; ")) + ")" : "") +
      "; with a planted fault (a loader that drops one row) " + (sp.pass ? "nothing failed, so do not trust this bench." : (sp.total - sp.held) + " properties fail, as they should.") +
      " Purchase times are read as Sao Paulo civil time; daylight-saving dates come from the IANA time zone database."));
    p.appendChild(el("p", "spm-attr", "Data: derived and masked from the Brazilian E-Commerce Public Dataset by Olist, Kaggle, licensed CC BY-NC-SA 4.0. No review text is used. Serai Commerce, its two warehouses, the drifts and the parity bar are constructed."));
    host.appendChild(p);
    render();
    root.SPM_LIVE = {
      setRung: function (i) { state.rung = i; render(); },
      setLoose: function (b) { state.loose = !!b; render(); },
      setBreak: function (b) { state.brk = !!b; render(); },
      current: function () { var R = current(); return { rung: state.rung, score: R.rungs[state.rung], all: R.all, perDrift: R.perDrift }; },
      selfTest: function () { return selfTest(D); }
    };
  }

  var api = { prep: prep, legacy: legacy, newWarehouse: newWarehouse, aggregate: aggregate, detail: detail,
    run: run, ladder: ladder, selfTest: selfTest, touched: touched, DRIFTS: DRIFTS, RUNGS: RUNGS, BAR: BAR, LOOSE: LOOSE };

  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.SPM_ENGINE = api;
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
    else init();
  }
})(typeof window !== "undefined" ? window : this);
