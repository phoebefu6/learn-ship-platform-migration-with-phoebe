# Source map - Ship It: Data Platform Migration (learn-ship-platform-migration-with-phoebe)

Internal build document. Never linked from an audience page. Built 2026-11-19 by Phoebe Fu's course
lead. Every number a page quotes comes from section 3 (bench canon) or section 4 (verified facts).
Tiers: **read at source** (the page was read in full or the quoted passage was read on the page),
**reported** (seen only in secondary coverage or a summary; say "reported" on the page or cut it).
Fast-moving tools (Data Validation Tool, reladiff, DuckDB): **re-verify before delivery**.

## 1. The question and the case

On cutover day, can you prove every number the business reads is the same, or say exactly why it changed?

Running case: **Serai Commerce** (constructed SEA social-commerce enabler, continued from
learn-ship-ecommerce-enabler and learn-ship-social-commerce; label "Constructed Serai Commerce
example" every time). Serai moves its warehouse from a **legacy** stack to a **new** one. Engines are
named as classes (a row-store legacy warehouse, a cloud columnar warehouse), never as a vendor
recommendation. Rows: the same **8,614 delivered Olist orders** (9,843 lines, 8,333 customers,
exports A/B/C = 3,935 / 2,912 / 1,767; item value BRL 1,197,842.24; freight BRL 195,579.02;
8,546 orders with a review score, 68 without, mean score 4.1390; 598 order days from 2016-10-04 to
2018-08-28; 21 months). Reproduced and asserted by `materials/build-spm-data.py`.

Running artifact: **Serai's migration runbook**, one section per session: inventory (a1, b1) ->
scope and sequence (a3, b2) -> translation rules (b3) -> parity suite and signed bar (a4, b4, b5)
-> historical reload (b6) -> parallel run (b7) -> cutover plan with rollback (a5, b8) -> week-after
watch (a6, b9) -> decommission log (a6) -> signed runbook (b10 capstone).

Constructed inventory facts (use exactly, label constructed): legacy estate 214 tables, 61 scheduled
jobs, 38 dashboards; query log of the last 90 days shows 131 tables read at least once, 83 tables
never read, 19 dashboards with no viewer in 90 days. Serai's warehouse move window: 10 weeks of
parallel run is NOT assumed; the parallel run is 4 weeks (constructed). These are teaching numbers,
not from any source; pages must say "constructed".

## 2. Seams (pick this side out loud, absolute https links, never reteach)

| Sibling | They own | We own | Link |
|---|---|---|---|
| learn-dataops b4 | schema migrations inside one database, migration tools in CI/CD | moving a whole platform | https://phoebefu6.github.io/learn-dataops-with-phoebe/courses/b4-dbops-migrations.html |
| learn-data-reliability a5, b5; learn-data-orchestration 05 | backfills as reliability work, idempotency | historical reload as one cutover step | https://phoebefu6.github.io/learn-data-reliability-with-phoebe/courses/b5-backfills.html , https://phoebefu6.github.io/learn-data-reliability-with-phoebe/courses/a5-backfills-and-debt.html , https://phoebefu6.github.io/learn-data-orchestration-with-phoebe/courses/05-backfills.html |
| learn-testing-data-ml-code 03 | data checks on real rows in one system | parity tests BETWEEN two systems | https://phoebefu6.github.io/learn-testing-data-ml-code-with-phoebe/courses/03-data-checks.html |
| learn-data-warehouse a4, b9 | buying a warehouse, lakehouse, modern stack | none: the target is given | https://phoebefu6.github.io/learn-data-warehouse-with-phoebe/courses/a4-buy-landscape.html , .../b9-lakehouse-modern-stack.html |
| learn-ship-social-commerce, learn-ship-ecommerce-enabler | Serai's data products, schema, value | none: reuse the schema | https://phoebefu6.github.io/learn-ship-social-commerce-with-phoebe/ , https://phoebefu6.github.io/learn-ship-ecommerce-enabler-with-phoebe/ |
| learn-data-observability | monitors on one table | the week-after comparison only | https://phoebefu6.github.io/learn-data-observability-with-phoebe/ |
| learn-runbooks-postmortems | how to write a runbook | the migration runbook's content | https://phoebefu6.github.io/learn-runbooks-postmortems-with-phoebe/ |

## 3. Bench canon (assets/spm-live.js = materials/spm_reference.py on 1,740 values, rel 1e-9)

Checked by `python3 -I materials/compare-ladder.py` (exit 0; planted 0.1% fault caught). Engine
selfTest 8 of 8 on the shipped data; with a planted lossy loader (one row dropped) 3 properties fail.

### The seven drifts (constructed rules on real rows), orders touched
| id | label on the widget | kind | orders touched |
|---|---|---|---|
| late | Late rows appended twice (delivered > 30 days after purchase) | defect | 367 |
| tz | Fixed -03:00 offset ignores daylight saving (00:00-00:59 civil time in Brazilian summer time moves to the previous day) | defect | 72 |
| nul | Missing review score loaded as 0 (NULL exported as empty string, cast to 0) | defect | 68 |
| idiv | Items per order by integer division | defect | all 8,614 (metric-level) |
| case | Case-sensitive customer-key join (Export C keys lower case) | defect | 1,767 |
| round | Freight split per line, rounded per line | accepted difference | 90 |
| float | Money summed as floating point | accepted difference | all 8,614 (metric-level) |
Plus a no-drift control. DST windows in the sample (IANA tz via zoneinfo): 2016-10-16 to
2017-02-18 and 2017-10-15 to 2018-02-17 (day index 46-170, 410-534).

### Checks
counts (total rows) · keys (missing, extra, duplicated keys; customer keys unresolved, both sides)
· daily (six metrics per day, exact; 598 days) · parity (six metrics per month against Serai's
signed bar; 21 months) · edge (595 orders placed within one hour of local midnight: same day in both?).
Six metrics: orders, item value (BRL), freight (BRL), items per order, reviewed orders, average review score.
Signed parity bar (constructed, monthly): orders exact; item value within 0.05%; freight within
0.05%; items per order within 0.005; reviewed orders exact; average review within 0.01.
Loose bar (anti-lever): 3% on every metric.

### Ladder (each drift planted alone; defects caught of 5 / missed / false alarms of 3)
| Rung | signed bar | loose bar | break (both sides read new) |
|---|---|---|---|
| 0 Row counts | 1 / 4 / 0 (late) | 1 / 4 / 0 | 0 / 5 / 0 |
| 1 + Keys | 2 / 3 / 0 (+ case) | 2 / 3 / 0 | 0 / 5 / 0 |
| 2 + Daily aggregates (exact) | 5 / 0 / 2 (round, float flagged) | 5 / 0 / 2 | 0 / 5 / 0 |
| 3 + Tolerances by metric (signed bar, monthly) | 4 / 1 / 0 (tz missed) | 3 / 2 / 0 (tz, nul missed) | 0 / 5 / 0 |
| 4 + Time-zone edge check | 5 / 0 / 0 | 4 / 1 / 0 (nul missed) | 0 / 5 / 0 |

### Per-drift detail (signed bar)
- late: rows 8,614 vs 8,981; 367 duplicated keys; daily orders differ on 205 of 598 days; parity
  fails all 21 months on orders. Item value BRL 1,197,842.24 becomes BRL 1,262,425.64.
- tz: rows equal, keys equal; daily orders differ on 74 days (item value 81 days); parity: 0 months
  fail (no shifted order crosses a month end in this sample); edge: 72 of 595 near-midnight orders
  on another day. Whole-sample totals unchanged.
- nul: reviewed orders 8,546 becomes 8,614; average review 4.1390 becomes 4.1063; daily: 63 days
  differ; parity: reviewed fails 20 months (largest gap 10 orders), average 19 months (largest gap 0.0931). Under the 3% loose bar: 0 months
  fail (largest monthly gap 2.22%, February 2017).
- idiv: items per order 1.1427 becomes 1 (whole sample, and every month); daily 427 days differ.
- case: rows equal; 1,767 customer keys unresolved in new vs 0 in legacy; no aggregate moves.
- round: freight BRL 195,579.02 becomes BRL 195,579.59; daily freight differs on 80 days; inside
  the 0.05% bar every month.
- float: item value differs on 302 days and freight on 269 in the last bits (largest monthly gap
  about 2e-10 BRL); exact equality on floating point flags them, any tolerance clears them.
- All seven at once: orders 8,981; item value BRL 1,262,425.64; freight BRL 206,704.26; items per
  order 1; reviewed 8,981; average review 4.0217. Every check alarms.
- Console: `SPM_LIVE.setRung(4); SPM_LIVE.current().score` -> caught 5, missed 0, falseAlarms 0.

## 4. Verified facts (tier, source number from the appendix)

Migration method (vendor claims, never recommendations)
- Google Cloud: "run the data validation tool to validate that your source and destination tables
  match." [S1] read at source.
- Google Cloud blog (2019): phases "Prepare and discover", "Assess and plan", "Execute"; "both your
  data warehouse and BigQuery can be actively used in parallel"; "At the end of each iteration,
  validate that the use case was successfully migrated according to your definition of done" [S2] read at source.
- AWS DMS: "compares each row in the source with its corresponding row at the target, verifies the
  rows contain the same data, and reports any mismatches." "Data validation requires that the table
  has a primary key or unique index." [S3] read at source.
Tooling (re-verify before delivery)
- Google Data Validation Tool lists column validation (count, sum, avg, min, max, stddev, group by),
  row validation, schema validation, custom query validation; row hashing with SHA256; release
  v8.10.2 on 2026-11-11 [S4] read at source.
- datafold/data-diff archived May 17, 2024; "Datafold is no longer actively supporting or developing
  open source data-diff." [S5] read at source.
- reladiff: "a fork of an archived project called data-diff"; "a divide-and-conquer algorithm, based
  on matching hashes, to efficiently identify modified segments"; 0.6.0 on 4 Mar 2025 (PyPI) [S6] read at source.
SQL semantics
- PostgreSQL: integer division "truncates the result towards zero"; 5 / 2 = 2 [S7] read at source.
- PostgreSQL timestamptz: "stored internally as UTC, and the originally stated or assumed time zone
  is not retained"; timestamp without time zone "will silently ignore any time zone indication" [S8].
- PostgreSQL: "Do not write expression = NULL because NULL is not 'equal to' NULL"; IS DISTINCT
  FROM is "Not equal, treating null as a comparable value" [S9] read at source.
- DuckDB: "When both operands are integers, / performs floating points division (5 / 2 = 2.5)";
  "// performs integer division (5 // 2 = 2)" [S10] read at source. The version in which this
  changed was NOT verified: never state it.
- DuckDB TIMESTAMPTZ values "are displayed with the UTC offset of the configured time zone" [S11].
- Oracle: "The database currently treats a character value with a length of zero as null", and this
  "may not continue to be true in future releases" [S12] read at source.
- MySQL 8.0: default utf8mb4 / utf8mb4_0900_ai_ci, "so nonbinary string comparisons are
  case-insensitive by default" [S13] read at source. (PostgreSQL default comparisons are
  case-sensitive: do NOT quote; teach as "many engines compare case-sensitively".)
- IANA tz database release 2019b (2019-07-01): "Brazil no longer observes DST." [S14] read at source.
Launches and rollback
- SRE book: "Almost all updates to Google's services proceed gradually, according to a defined
  process"; "If the change doesn't pass the validation period, it's automatically rolled back.";
  "The checklist proved to be a useful tool for ensuring reproducibly reliable launches." [S15] read at source.
- SRE Workbook: canarying is "a partial and time-limited deployment of a change in a service and its
  evaluation"; if it looks bad, "pause and roll back the deployment." [S16] read at source.
Postmortems
- TSB (Bank of England, 20 Dec 2022): fined "a total of £48,650,000"; TSB "failed to organise and
  control the IT migration programme adequately." [S17] read at source. The FCA/PRA split is reported only.
- TSB's own release on the Slaughter and May review (published 19 Nov 2019): the review raised
  "questions around how testing was carried out"; go-live "followed a long period of testing, with
  reports to the Board signalling readiness." [S18] read at source. The report PDF itself was NOT
  read: any finding attributed to it is "reported".
- GitHub, 21 Oct 2018: connectivity "restored in 43 seconds"; the database "contained writes that
  were not present in the other data center"; "degraded service for 24 hours and 11 minutes";
  chose to "prioritize data integrity over site usability and time to recovery." [S19] read at source.
Data
- Olist: "100k orders from 2016 to 2018 made at multiple marketplaces in Brazil"; "This is real
  commercial data, it has been anonymised"; CC BY-NC-SA 4.0 [S20] read at source (Kaggle API view).

Contested or unknown (teach the disagreement, never resolve): big bang vs phased cutover (vendors
recommend iterative; TSB shows the cost of a single large switch, but one case is not a base rate);
how long a parallel run should last (no source gives a number: Serai's 4 weeks is constructed);
whether row hashing or aggregates is "enough" (DVT offers both, AWS DMS goes row by row and needs a
key): the answer depends on the cost of a missed row, which is a business call.

## 5. Per-session coverage

Leader (no code)
- a1 Why migrations break the numbers: the failure modes as the bench's seven drifts; TSB and GitHub
  as real-world stories; "done" = every number read is the same or explained; the ladder headline.
- a2 Inventory before plan: what you own, who reads it, what nobody reads (constructed 214/131/83/19);
  vendors' "assess and plan" phase [S2]; retire before you move.
- a3 Lift, rebuild or retire: per asset decision; big bang vs parallel / iterative [S2] vs TSB [S17,S18]; contested.
- a4 The parity bar: accepted differences signed in advance (round, float); the trade (rung 2 vs 3);
  loose bar anti-lever numbers; DVT/AWS DMS as classes of tool [S3,S4].
- a5 Cutover day and the rollback: go/no-go, freeze, rollback criteria; SRE gradual rollout and
  automatic rollback [S15,S16]; GitHub's integrity-over-recovery choice [S19].
- a6 The week after and switching off: drift watch (tz drift hides in monthly numbers), decommission
  log, the cost case closed only when legacy is off; the break button lesson (a clean report means
  nothing until you know what each side read).
Builder
- b1 Inventory from the query log: usage and lineage from logs; dead assets; DuckDB build-along on a
  constructed query log.
- b2 The dependency graph and the order of moves: topological order; sources first (wave 0), sinks last.
- b3 Translate the SQL: dates, time zones [S8,S11,S14], NULL [S9,S12], integer division [S7,S10],
  collation [S13]; the five drifts that come from translation.
- b4 Row and key parity: counts and keys catch late and case (rung 0 and 1); AWS DMS needs a key [S3].
- b5 Aggregate parity at the grain people read: rungs 2 and 3, tolerances by metric; float and round.
- b6 Historical reload: reload as a cutover step; late rows (367); link backfill siblings.
- b7 Parallel run: two systems, one truth, the diff dashboard; daily vs monthly views.
- b8 Cutover rehearsal and rollback: rehearse, time it, rollback trigger list; SRE [S15,S16].
- b9 The week after: drift that hides: tz drift 72 orders, 74 days, 0 months; edge check; Brazil DST end [S14].
- b10 The parity bench: full ladder, loose bar, break; capstone signed runbook.

## 6. Not covered (honest list)
Choosing the target platform (learn-data-warehouse owns it); schema migrations inside one database
(learn-dataops b4); writing craft of runbooks (learn-runbooks-postmortems); monitor design
(learn-data-observability); cost modelling of cloud warehouses with real prices (no verified
numbers); streaming / CDC replication mechanics beyond naming the class; any vendor's tool walk-through;
security and access migration (permissions, row-level policies) beyond a checklist line.

## 7. Citation appendix
- [S1] Google Cloud, "Introduction to BigQuery migration", https://docs.cloud.google.com/bigquery/docs/migration/migration-overview (read 2026-11-19).
- [S2] Cueva and Saxby, "Migrating Teradata and other data warehouses to BigQuery", Google Cloud blog, 7 Aug 2019, https://cloud.google.com/blog/products/data-analytics/migrating-teradata-and-other-data-warehouses-to-bigquery/
- [S3] AWS, "AWS DMS data validation", https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Validating.html
- [S4] GoogleCloudPlatform/professional-services-data-validator, https://github.com/GoogleCloudPlatform/professional-services-data-validator
- [S5] datafold/data-diff (archived), https://github.com/datafold/data-diff
- [S6] erezsh/reladiff, https://github.com/erezsh/reladiff
- [S7] PostgreSQL docs, "Mathematical Functions and Operators", https://www.postgresql.org/docs/current/functions-math.html
- [S8] PostgreSQL docs, "Date/Time Types" 8.5.1.3, https://www.postgresql.org/docs/current/datatype-datetime.html
- [S9] PostgreSQL docs, "Comparison Functions and Operators", https://www.postgresql.org/docs/current/functions-comparison.html
- [S10] DuckDB docs, "Numeric Functions", https://duckdb.org/docs/2.0/sql/functions/numeric.html
- [S11] DuckDB docs, "Timestamp Types", https://duckdb.org/docs/2.0/sql/data_types/timestamp.html
- [S12] Oracle Database 23 SQL Language Reference, "Nulls", https://docs.oracle.com/en/database/oracle/oracle-database/23/sqlrf/Nulls.html
- [S13] MySQL 8.0 Reference Manual, "Case Sensitivity in String Searches", https://dev.mysql.com/doc/refman/8.0/en/case-sensitivity.html
- [S14] IANA tz database NEWS, release 2019b, https://data.iana.org/time-zones/tzdb/NEWS
- [S15] Google SRE book, "Reliable Product Launches at Scale", https://sre.google/sre-book/reliable-product-launches/
- [S16] Google SRE Workbook, "Canarying Releases", https://sre.google/workbook/canarying-releases/
- [S17] Bank of England, "TSB fined for operational resilience failings", 20 Dec 2022, https://www.bankofengland.co.uk/news/2022/december/tsb-fined-for-operational-resilience-failings
- [S18] TSB, news release on the Slaughter and May review, https://www.tsb.co.uk/news-releases/slaughter-and-may/
- [S19] Jason Warner, "October 21 post-incident analysis", GitHub blog, 30 Oct 2018, https://github.blog/news-insights/company-news/oct21-post-incident-analysis/
- [S20] Olist, "Brazilian E-Commerce Public Dataset by Olist", Kaggle, CC BY-NC-SA 4.0, https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
