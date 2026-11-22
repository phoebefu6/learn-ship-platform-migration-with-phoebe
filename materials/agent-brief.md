# Agent brief - shared by every fan-out page of learn-ship-platform-migration-with-phoebe

Internal build document, filled from `~/.claude/skills/course-builder/references/agent-brief.template.md`
on 2026-11-19. Never link it from an audience page.

You are writing ONE static HTML session page. No servers, no npm. **If your target file already
exists on disk, do not write it; report that and stop.** Write the file, return its path and one
line of coverage, plus any source you read that the map lacks and any contradiction you found with
another page. No HTML in your reply. Never touch any other file in the repo.

REPO = `/Users/phoebe.fu/Documents/claude_work/github_repo/learn-ship-platform-migration-with-phoebe`

## Read first, in this order

1. The template page for YOUR track. Copy its structure, classes, SVG grammar and quiz markup
   EXACTLY, including how many options each question has (FOUR, A to D):
   - Leader (a2-a6): `REPO/courses/a1-why-migrations-break-the-numbers.html`
   - Builder (b2-b9): `REPO/courses/b1-inventory-from-the-query-log.html`
   - For bench numbers and the widget's wording, also read `REPO/courses/b10-the-parity-bench.html`.
2. The source map: every verified number, its evidence tier, per-session coverage, the seams. Use
   ONLY its numbers; never invent a statistic; if a fact is missing, teach the uncertainty.
   `REPO/materials/official-course-map.md` (section 3 is the bench canon, section 4 the verified facts).
3. The stylesheet `:root` block for the palette tokens: `REPO/assets/style.css` (first 30 lines).

## Page skeleton (keep every component)

toolbar (crumb EXACTLY `<a href="../index.html">learn-ship-platform-migration-with-phoebe</a> / Leader
session N of 6` or `... / Builder session N of 10`, #toggle-all, #zoom-toggle) · masthead (eyebrow
"Ship It: Data Platform Migration · Leader session N of 6" or "· Builder session N of 10", h1 with
one `<span class="accent">`, .sub, .chip-row with the level chip given in your outline plus two
audience chips and "45 min", .agenda a1-a4) · main.wrap · section#intro (Part 0: kicker with h2
"Where this session sits" or similar, .lede, .legend pills copied from the template, .callout.win
"★ What you walk out with tonight.") · 3 Parts, each `section.section#part-N` with section-kicker
(klabel "Part N · covers ...", h2, `.tag.concept "N min live"`), a `.lede`, ONE figure,
`details.card` accordions (summary: `.mode.live` or `.mode.self`, title, `.mini`, `.caret ▶`), at
least one `.callout.example` with `span.ex-pill` "Real world" on the page (one per Part is the
norm) · section#demo-1 Build-along (kicker `.tag.demo "★ 22 min · everyone builds"`, leader pages
may use 20; .lede, ONE figure, `.steps > .step`, each step a `p` with a `.prompt-box.good` carrying
a `span.label` BELOW the p where it has one) · section#exercise Homework (ol, 4 items) ·
section#quiz (3 x `.quiz-q data-answer="0-based"`, `p.qtext`, FOUR `button.qopt` "A · ...",
`p.qwhy`; one `p.quiz-score` after the last; vary the correct letter) · section#official, h2 EXACTLY
"What this session teaches, and where it came from", `.covered > .covered-row` (pill solid ✓ /
light ◐ + name + note), then the `.mono` line EXACTLY "Every fact on this page, and its verification
tier, is recorded in the course's source map." · section.cheat#cheatsheet (h3 "Leader session N cheat
sheet <span>· pin this</span>" or "Builder session N cheat sheet ...", .grid-2 of six .cheat-item) ·
`.callout.next` with `.nx-pill` "Next session" · footer.pagefoot · `<script src="../assets/app.js?v=1"></script>`.

Head: the template's social meta block with this page's own description/title/url;
`<title>Leader session N · TITLE - learn ship platform migration with phoebe</title>` (Builder
likewise); `<link rel="stylesheet" href="../assets/style.css?v=1">`. Nothing else external.

First `details.card` in the FIRST Part is `open`; no other. Sentence case headings. Warm
practitioner voice, concrete, never dry. Inside prompt-boxes escape `&` `<` `>`. 450 to 650 lines
is guidance about depth, never a target: never collapse whitespace, dissolve a list into a
paragraph, or drop a component to fit. A "bad" example box uses `.prompt-box.bad` with a plain-words
label: NEVER a cross mark (no ✗ ✘ ✕ ❌ ×) anywhere on the page; label states in words.

## Hard rules (a violation is rework)

- NEVER an em dash or en dash, anywhere (prose, code, aria-labels, comments). Hyphen only.
- No meta text: never "this course", "in this course", "the course teaches", "banned here". State
  the professional norm directly with its reason. The two exact estate phrases above are the only
  self-references; "session 5" and "Builder session 10" cross-references are fine.
- Attribution "by Phoebe Fu". Never "built with" a tool.
- Every number comes from the map or is labelled constructed. Bench numbers must be ones the b10
  widget prints (map section 3), in its words. Never invent a percentage, a cost, a duration or an
  industry statistic. Constructed Serai figures not in the map: label "constructed" on the page and
  keep them few (e.g. rehearsal timings, a freeze window length). No real cloud prices.
- Builder build-alongs run in DuckDB. You MUST run every SQL you print, with `python3 -I` and the
  `duckdb` module, from your own scratch dir `/private/tmp/claude-504/spm/agents/<page-code>/`
  (never the repo), and quote outputs only as printed. If a construct errors in DuckDB, change the
  SQL, do not print an invented result. Keep build-along data small and constructed, labelled
  "Constructed Serai Commerce example".
- Contested or missing evidence: teach the disagreement; never resolve it. Contested here: big bang
  vs phased cutover; how long a parallel run should last (no source gives a number; Serai's 4 weeks
  is constructed); row hashing vs aggregates as "enough".
- Citations in the exact form of the map's appendix; anything marked reported is "reported". The
  TSB Slaughter and May report itself was NOT read: never attribute a specific finding to it.
- NEVER "lottery" or "lotteries"; say the mechanism.
- Default to the English word. A Chinese term that is genuinely a name carries its English in
  brackets right after it, every occurrence.
- Engines and tools: name warehouse engines as CLASSES (a row-store legacy warehouse, a cloud
  columnar warehouse), never as a recommendation. Vendor docs are quoted as "vendor claims". The SQL
  engines whose documentation the map quotes (PostgreSQL, DuckDB, Oracle, MySQL) and open-source
  tools in the map (Google's Data Validation Tool, reladiff, data-diff) may be named for what their
  docs say. Olist is named as the data source only.
- Titles, widget ids and class names must not collide with siblings. Banned prefixes: `spm-` (the
  bench's), `ssc-`, `tw-`. The word "bench" must not appear in any h1/h2 except on b10. Do not reuse
  these sibling headings: "A green pipeline is not evidence", "Backfills and debt", "Two ways to run
  the past", "Expand-contract and rollback", "Migration tools", "Run the ladder yourself", "What the
  bench measures", "Lineage and ...", "Count what you have", "The limits, stated honestly".
- Serai Commerce is constructed: write "Constructed Serai Commerce example" where it first appears.
  Orders are real derived Olist rows (CC BY-NC-SA 4.0); never quote review TEXT (scores only).
- Never Phoebe's own employers, clients or projects; never a real company as Serai.
- Light surfaces only: no dark band, no dark code box you add, no dark figure panel.
- Seams: link with absolute https URLs from the map's section 2, say which side this page owns, never
  reteach the sibling's subject (idempotency, monitor design, runbook writing craft, target choice).

## Figure grammar (hand-drawn, every figure)

Palette, ONLY these hexes (no invented greys): ink `#231C12` · muted `#5E5446` · faint `#D6CDBE` ·
hairline `#ECE6DB` · primary brown-gold `#624818` (strokes, hachure, white text only on it) · deep
`#46330F` (accent text, values) · mid `#85621F` · soft `#E3D3B0` · tint `#F8F2E6` · signal blue
`#9CC3E6` (fill ONLY, ink text on it, the one thing the figure is about) · blue ink `#173E66`
(text) · blue tint `#EAF3FB` · paper `#FDFBF7` · `#FFFFFF` · universal reds `#991B1B` `#FEF2F2`
`#FCA5A5` only for a wrong-way panel, a missed defect or a false alarm.

- `<figure class="zoomable">` > `<svg viewBox="0 0 880 H" xmlns="http://www.w3.org/2000/svg"
  role="img" aria-label="the data, not the shape">` > `<defs>` + `<style>` + content, then
  `<figcaption>🔍 Click to zoom - takeaway</figcaption>`. Grow H, never W.
- Prefix unique per figure, used for every class and id: page code + letter, e.g. `a2a`, `a2b`,
  `b5c`, `b9d` (so `a2aSk`, `a2aHc`, `a2aAr`, `.a2aH`).
- `<defs>` holds, with figure prefix P: a wobble filter `id="PSk"` (`feTurbulence
  type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="<int>"` + `feDisplacementMap
  scale="2.4" xChannelSelector="R" yChannelSelector="G"`, `x="-3%" y="-3%" width="106%"
  height="106%"`), a hachure pattern `id="PHc"` if used (7x7 userSpaceOnUse, rotate(-38), one
  `#624818` line, opacity .5), an open arrowhead `id="PAr"` if used (path `M1 1 L9 5 L1 9`, fill
  none, `#231C12` stroke 1.6). ALL shapes sit inside ONE `<g filter="url(#PSk)" fill="none"
  stroke="#231C12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">`; rects carry a
  tiny rotation (under 1 degree for panels, up to 4 for hand-placed items). Fills: white, tint, the
  hachure for "the pile" or "the data" (never under text), and signal blue ONLY for the one thing
  the figure is about. Text classes: `.PH` 800 12px ink heading · `.PL` 600 11-12px ink label ·
  `.PS` 400 11px muted · `.PB` 800 11-12px `#173E66` · `.PV` 800 16px `#46330F` value · `.PA` 700
  11px `#46330F` axis caption · `.PR` 800 11px `#991B1B` · `.PN` 400 12px muted note.
- ALL `<text>` outside any filtered group, Inter sans stack, never below 11px.
- Fit (owner: `diagram-kit.md`): max chars ≈ (box width - 20) / 7 at 12px, 6.4px/char at 11px;
  full-width note under 110 chars; 40px between neighbouring labels; bottom note 22px below the
  last shape, H clears it by 8px. No path, arrow or gridline may cross a label (the gate flags
  line-through-text and text-out-of-box). Hand-stacked items must not overlap as painted rects.
  When in doubt, shorten.
- Floor: one figure per Part plus one in the build-along (4 figures). Draw the MECHANISM (a row
  appended twice by a late feed; a fixed offset moving 00:30 to 23:30 the day before; a recursive
  walk assigning waves; a pointer swap for rollback; a tolerance band around a gap), never a
  metaphor, never decoration.

## Voice and honesty

Every Part gets a real-world story from the map's section 4 (TSB 2018 and the 2022 fine; GitHub 21
October 2018; Google SRE launches and canarying; vendor validation docs; SQL engine docs; IANA
2019b). Quote at most short phrases, exactly as in the map, in double quotes. Constructed cases say
"constructed". "Your numbers will differ" only where the learner uses their own estate.

## Cross-links (absolute URLs)

From the map's section 2, plus:
- Bench: `b10-the-parity-bench.html` (relative within courses/), leader done sheet `a1-why-migrations-break-the-numbers.html`.
- Hub: https://phoebefu6.github.io/learn-with-phoebe/

## Footer chains and session titles (exact; h1 carries one accent span you choose)

Footer left: `Leader session N of 6 · learn-ship-platform-migration-with-phoebe · by Phoebe Fu &nbsp;·&nbsp; 📚 <a href="https://phoebefu6.github.io/learn-with-phoebe/">Learn with Phoebe ↗</a>` (Builder likewise).
Footer right: `<a href="PREV.html">← Prev: PREV TITLE</a> &nbsp;·&nbsp; <a href="NEXT.html">Next: NEXT TITLE →</a>`;
a6: `← Prev: Cutover day and the rollback` and `<a href="../index.html">Course home</a>`.

Leader: a1-why-migrations-break-the-numbers.html "Why migrations break the numbers" · a2-inventory-before-plan.html
"Inventory before plan" · a3-lift-rebuild-or-retire.html "Sequence and scope: lift, rebuild or retire" ·
a4-the-parity-bar.html "The parity bar" · a5-cutover-day-and-the-rollback.html "Cutover day and the rollback" ·
a6-the-week-after-and-switching-off.html "The week after and switching off".
Builder: b1-inventory-from-the-query-log.html "Inventory from the query log" · b2-the-dependency-graph.html
"The dependency graph and the order of moves" · b3-translate-the-sql.html "Translate the SQL" ·
b4-row-and-key-parity.html "Row and key parity" · b5-aggregate-parity.html "Aggregate parity at the
grain people read" · b6-historical-reload.html "Historical reload" · b7-parallel-run.html "Parallel run" ·
b8-cutover-rehearsal-and-rollback.html "Cutover rehearsal and rollback" · b9-drift-that-hides.html
"The week after: drift that hides" · b10-the-parity-bench.html "The parity bench".

Runbook sections (Builder track; leader pages refer to them): 1 inventory (b1) · 2 order of moves (b2)
· 3 translation rules (b3) · 4 parity suite and bar (b4, b5, b10) · 5 historical reload (b6) ·
6 parallel run (b7) · 7 cutover and rollback (b8) · 8 the week after (b9).

## Per-page outlines

### a2 Inventory before plan (🟡 Intermediate; audience: heads of data and platform owners)
Part 1 what you own: Serai's constructed full estate (214 tables, 61 jobs, 38 dashboards; 90-day log:
131 read, 83 never read; 19 of 38 dashboards no viewer), all labelled constructed; figure: the estate
narrowing from what exists to what is read to what people read. Part 2 who reads it: each number on
the a1 done sheet gets a reader and a signer; figure: numbers to readers to signers. Part 3 what
nobody reads: retire before you move, because every retired table removes translate, reload and
prove; two-step retirement (stop and revoke with a date, then archive and drop); figure: cost of a
table moved vs retired. Real world: Google 2019 blog phases "Prepare and discover", "Assess and plan"
(vendor claim); TSB readiness quote. Build-along: the leader's inventory sheet (status, reader,
signer, retire date) for Serai's 14 tables from Builder session 1 (move 5, move as a dependency 6,
retire candidates 3, names in b1). Quiz: why count reads not tables; why job-only tables move; why
the 90-day window is a judgement. Next: a3.

### a3 Sequence and scope: lift, rebuild or retire (🟡 Intermediate)
Part 1 one decision per asset (lift = translate as is; rebuild = redesign for the target; retire);
criteria (who reads it, how complex its SQL, whether it carries one of the seven drifts); figure:
decision tree. Part 2 big bang vs phased with a parallel run: Google 2019 blog "both your data
warehouse and BigQuery can be actively used in parallel" (vendor claim) vs the single-switch risk
in TSB (one case is not a base rate); CONTESTED, teach both sides; figure: two timelines. Part 3 the
order of moves: retirements first, then waves in dependency order from the b1 lineage (raw and ref,
then staging, then marts, then reports); figure: waves. Seam: choosing the target platform belongs to
learn-data-warehouse a4 (link), the target is given. Build-along: Serai's scope sheet: the 14 tables,
each lift, rebuild or retire, with a wave. Next: a4.

### a4 The parity bar (🟠 Advanced-practical)
Part 1 accepted differences, signed before anyone looks: freight split per line (90 orders, freight
BRL 195,579.02 vs BRL 195,579.59), floating-point money (differs on 302 days of item value in the last
bits); figure: Serai's bar as metric / tolerance / absorbs / must still catch (orders exact; item value
0.05%; freight 0.05%; items per order 0.005; reviewed orders exact; average review 0.01). Part 2 exact
daily vs the signed monthly bar: rung 2 5 of 5 with 2 false alarms, rung 3 4 of 5 with 0; the
fixed-offset drift moves 72 orders, 74 days, 0 months; figure: two-number headline per rung. Part 3 a
bar too loose: 3% on every metric hides the missing-review drift (largest monthly gap 2.22%), rung 4
falls to 4 of 5 (rung 3 to 3 of 5); and the break (both sides on the new warehouse) 0 of 5; figure:
gap against two bars. Real world: AWS DMS row comparison needs a key; Google DVT aggregates and hashes
(vendor claims; tools report differences, people sign which ones block). Build-along: the bar sheet a
leader signs: metric, grain read, tolerance, absorbs, must catch, signer. Next: a5.

### a5 Cutover day and the rollback (🟠 Advanced-practical)
Part 1 go/no-go: done sheet with no "open", rung-4 parity report naming both targets and the bar,
rehearsal done (Builder 8), rollback tested; figure: go/no-go decision tree. Part 2 the freeze: freeze
changes on legacy, last delta load, final parity run, switch readers, announce; figure: a cutover-day
timeline (hours constructed and labelled). Part 3 rollback criteria written while calm: numeric
triggers tied to the done sheet, who pulls it, how long the legacy stays ready; SRE book "Almost all
updates to Google's services proceed gradually..." and "If the change doesn't pass the validation
period, it's automatically rolled back."; SRE Workbook canarying "a partial and time-limited
deployment..."; GitHub "prioritize data integrity over site usability and time to recovery"; TSB fine
and readiness quote; figure: the rollback trigger mechanism. Build-along: Serai's go/no-go and
rollback sheet. Next: a6.

### a6 The week after and switching off (🔴 Advanced)
Part 1 drift watch: the fixed-offset drift (72 orders, 74 days, 0 months; 595 near-midnight orders,
72 on another day), IANA 2019b "Brazil no longer observes DST"; late rows (367 delivered more than 30
days after purchase); the watch ends on a written condition; seam: monitor design belongs to
learn-data-observability (link); figure: daily vs monthly view of the same drift. Part 2 the
decommission log: read-only legacy, final snapshot and archive, revoke, switch off, record each step
with a date and owner; figure: the decommission steps. Part 3 the cost case closed: during the
parallel run you pay for two systems; the saving starts only when legacy is off (qualitative, no real
prices); a clean report means nothing until you know what each side read (break: 0 of 5); figure: two
cost lines that only separate at switch-off (shape only, no numbers, labelled illustrative). Build-
along: Serai's week-after watch list and decommission log. Footer: prev a5, Course home.

### b2 The dependency graph and the order of moves (🟡 Intermediate)
Use the b1 log's 11 edges (copy the b1 setup or create an `edges` table with the same 11 rows). Part
1 the graph (nodes, edges, sources, sinks); figure. Part 2 order by depth: a recursive CTE (`WITH
RECURSIVE`) computing each table's longest path from a source = its wave; cycle detection (a guard on
path length or a visited list); figure: the recursive walk assigning waves. Part 3 waves of moves:
retire first (remove scorecard_v1 and the two other retire candidates from the graph), then waves 0,
1, 2, 3; each wave proved before the next; figure: waves as columns. Build-along in DuckDB: the
recursive CTE and the wave list; RUN IT and print the real output. Seam: orchestration DAGs belong to
learn-data-orchestration (link to its 02 or home page only if it exists). Next: b3.

### b3 Translate the SQL (🟡 Intermediate)
Four dialect gaps, each one of the bench's drifts, each run in DuckDB: integer division (PostgreSQL
"truncates the result towards zero"; DuckDB `/` on integers gives 2.5 and `//` gives 2: run both);
NULL (PostgreSQL "Do not write expression = NULL..."; IS DISTINCT FROM; Oracle treats a zero-length
string as null; show NULL vs '' vs 0 in a CAST: run it); time zones (named zone vs fixed offset: DuckDB
TIMESTAMPTZ / AT TIME ZONE 'America/Sao_Paulo' needs the ICU extension: test it; if unavailable say
so and show the arithmetic instead); collation (MySQL default "case-insensitive by default"; DuckDB
string equality: run 'abc' = 'ABC' and a fix with lower()). Parts: 1 numbers (division, rounding,
float vs DECIMAL), 2 NULL and empty, 3 time and text. Build-along: a translation-rules list (runbook
section 3) with each rule's test query. Next: b4.

### b4 Row and key parity (🟡 Intermediate)
Part 1 counts: rung 0 catches 1 of 5 (rows 8,614 vs 8,981, only the late rows); figure: which drifts
change a count. Part 2 keys both ways: missing, extra, duplicated (367), customer keys unresolved
(1,767 from the case-sensitive join), rung 1 2 of 5; AWS DMS validation needs a primary key or unique
index; figure: a full outer join on keys sorting rows into both, legacy only, new only, duplicated.
Part 3 what keys cannot see (values, days): sets up b5; figure. Build-along in DuckDB on a small
constructed legacy/new pair (10 to 20 rows) planting a duplicate, a missing key and a lower-cased key:
count, FULL OUTER JOIN key diff, duplicate count, FK resolution; RUN IT. Seam: single-system checks
belong to learn-testing-data-ml-code 03 (link). Next: b5.

### b5 Aggregate parity at the grain people read (🟠 Advanced-practical)
Six metrics (orders, item value, freight, items per order, reviewed orders, average review score).
Part 1 daily exact: 598 days; the late rows differ on 205 days; integer division on 427; NULL as 0 on
63; the fixed offset on 74 (orders); rung 2 5 of 5 with 2 false alarms (freight 80 days; float 302
item value / 269 freight); figure. Part 2 tolerance by metric at the monthly grain (21 months): the
signed bar; why a count is exact and money relative; figure: tolerance bands. Part 3 floating point
and rounding: float vs DECIMAL in DuckDB (RUN a sum that differs), per-line rounding; figure. Build-
along in DuckDB on small constructed daily aggregates: FULL OUTER JOIN on day, per-metric tolerance
test, a report of failing buckets; RUN IT. Next: b6.

### b6 Historical reload (🟠 Advanced-practical)
Part 1 reload as one cutover step: history moved in windows (by month: 21 in the sample), each window
followed by a parity run; seam: backfill mechanics and idempotency belong to learn-data-reliability b5
and a5 and learn-data-orchestration 05 (link, never reteach); figure. Part 2 late rows: 367 orders
delivered more than 30 days after purchase come back on the late feed; append makes 8,981 rows,
merge on key keeps 8,614; figure: append vs merge. Part 3 reload, then check: rung 1 catches the
duplicates (367 duplicated keys); figure. Build-along in DuckDB: a small table with a primary key,
INSERT of a late row (append into a keyless table vs INSERT ... ON CONFLICT DO UPDATE into a keyed
one); RUN IT and print real outputs. Next: b7.

### b7 Parallel run (🟠 Advanced-practical)
Part 1 two systems, one truth: legacy stays the system of record until cutover; Google 2019 blog
"actively used in parallel" (vendor claim); figure: both fed from the same sources, readers still on
legacy. Part 2 the nightly diff: the rung-4 suite every night, output as one row per check per night
(the diff dashboard); figure. Part 3 exit criteria: how long is contested (no source gives a number;
Serai's 4 weeks is constructed); exit on a written rule (e.g. N consecutive clean nights, every open
item closed); cost of running two; figure. Build-along in DuckDB: a constructed `nightly_diff` table
(a few nights x checks) and the query that answers "are we clean, and since when"; RUN IT. Next: b8.

### b8 Cutover rehearsal and rollback (🔴 Advanced)
Part 1 rehearse end to end on a copy, time each step (Serai timings constructed and labelled); figure:
rehearsal timeline. Part 2 the rollback is a pointer swap: readers query a view; cutover repoints it
to new, rollback repoints it to legacy, legacy kept loaded and read-only for an agreed window; SRE
quotes on gradual rollout and automatic rollback, canarying "partial and time-limited"; figure: the
view swap. Part 3 rehearse the rollback as hard as the move; triggers from the done sheet; GitHub's
integrity-first choice; TSB; figure. Build-along in DuckDB: two schemas or tables (legacy_orders,
new_orders), `CREATE OR REPLACE VIEW reporting_orders AS ...` swapped forward and back, with a count
query after each swap; RUN IT. Next: b9.

### b9 The week after: drift that hides (🔴 Advanced)
Part 1 time-zone edges: the fixed -03:00 offset moves 72 orders placed 00:00 to 00:59 during the two
Brazilian summers (DST windows 2016-10-16 to 2017-02-18 and 2017-10-15 to 2018-02-17) to the day
before: 74 daily numbers change, 0 monthly; IANA 2019b "Brazil no longer observes DST"; figure: 00:30
becoming 23:30. Part 2 the edge check: 595 orders within an hour of local midnight, 72 on another day;
rung 3 misses, rung 4 catches; figure. Part 3 late data and caches: the late feed (367 rows); a report
cache or extract that still serves legacy numbers after cutover (qualitative, no invented numbers);
the watch list and when it ends; seam: monitor design belongs to learn-data-observability (link);
figure. Build-along in DuckDB: a handful of constructed orders near midnight in January 2017,
converted with a named zone (ICU, test it) and with a fixed offset, and the edge-check query that
finds the mismatches; RUN IT (if ICU cannot load, do the conversion with an explicit DST-window table
and say so). Next: b10.
