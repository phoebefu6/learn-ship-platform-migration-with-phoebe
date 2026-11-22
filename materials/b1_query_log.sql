-- b1 build-along: Serai's constructed query log (Constructed Serai Commerce example). Run in DuckDB.
CREATE OR REPLACE TABLE tables AS SELECT * FROM (VALUES
 ('raw.orders_export_a'),('raw.orders_export_b'),('raw.orders_export_c'),('raw.reviews'),
 ('ref.state_region'),('stg.orders'),('stg.reviews'),('mart.orders_daily'),('mart.orders_monthly'),
 ('mart.brand_review'),('mart.seller_scorecard_v1'),('mart.seller_scorecard_v2'),
 ('mart.region_sales_2019'),('tmp.orders_backup_2017')) t(table_name);

CREATE OR REPLACE TABLE query_log AS SELECT query_id, CAST(run_at AS DATE) AS run_at, actor, action, table_name FROM (VALUES
 (1,'2026-11-14','job:build_stg','read','raw.orders_export_a'),
 (1,'2026-11-14','job:build_stg','read','raw.orders_export_b'),
 (1,'2026-11-14','job:build_stg','read','raw.orders_export_c'),
 (1,'2026-11-14','job:build_stg','write','stg.orders'),
 (2,'2026-11-14','job:build_stg','read','raw.reviews'),
 (2,'2026-11-14','job:build_stg','write','stg.reviews'),
 (3,'2026-11-14','job:build_marts','read','stg.orders'),
 (3,'2026-11-14','job:build_marts','write','mart.orders_daily'),
 (4,'2026-11-14','job:build_marts','read','mart.orders_daily'),
 (4,'2026-11-14','job:build_marts','write','mart.orders_monthly'),
 (5,'2026-11-14','job:build_marts','read','stg.orders'),
 (5,'2026-11-14','job:build_marts','read','stg.reviews'),
 (5,'2026-11-14','job:build_marts','read','ref.state_region'),
 (5,'2026-11-14','job:build_marts','write','mart.brand_review'),
 (6,'2026-11-14','job:build_marts','read','stg.orders'),
 (6,'2026-11-14','job:build_marts','write','mart.seller_scorecard_v2'),
 (7,'2026-11-14','job:build_marts','read','stg.orders'),
 (7,'2026-11-14','job:build_marts','write','mart.seller_scorecard_v1'),
 (8,'2026-11-01','dash:board_pack','read','mart.orders_monthly'),
 (9,'2026-11-14','dash:ops_daily','read','mart.orders_daily'),
 (10,'2026-11-13','dash:ops_daily','read','mart.orders_daily'),
 (11,'2026-11-03','dash:brand_review','read','mart.brand_review'),
 (12,'2026-10-20','user:analyst_1','read','mart.seller_scorecard_v2'),
 (13,'2026-09-02','user:analyst_2','read','stg.orders'),
 (14,'2026-05-10','user:analyst_1','read','tmp.orders_backup_2017'),
 (15,'2026-03-01','job:old_export','read','mart.region_sales_2019')
) q(query_id, run_at, actor, action, table_name);

-- The four queries, separated by ';;' for materials/run_sql.py
SELECT table_name,
       count(*) FILTER (WHERE action = 'read') AS reads,
       count(DISTINCT actor) FILTER (WHERE action = 'read') AS readers,
       max(run_at) FILTER (WHERE action = 'read') AS last_read
FROM query_log
WHERE run_at > DATE '2026-11-15' - INTERVAL 90 DAY
GROUP BY table_name
ORDER BY reads DESC, table_name;;
SELECT t.table_name
FROM tables t
LEFT JOIN query_log q
  ON q.table_name = t.table_name AND q.action = 'read'
 AND q.run_at > DATE '2026-11-15' - INTERVAL 90 DAY
WHERE q.query_id IS NULL
ORDER BY t.table_name;;
SELECT DISTINCT r.table_name AS source, w.table_name AS target
FROM query_log r
JOIN query_log w ON w.query_id = r.query_id AND w.action = 'write'
WHERE r.action = 'read'
ORDER BY target, source;;
SELECT table_name,
       bool_or(actor NOT LIKE 'job:%') AS read_by_people
FROM query_log
WHERE action = 'read' AND run_at > DATE '2026-11-15' - INTERVAL 90 DAY
GROUP BY table_name
ORDER BY read_by_people DESC, table_name

;;
WITH r AS (
  SELECT table_name, bool_or(actor NOT LIKE 'job:%') AS people
  FROM query_log
  WHERE action = 'read' AND run_at > DATE '2026-11-15' - INTERVAL 90 DAY
  GROUP BY table_name
)
SELECT CASE WHEN r.people THEN 'move'
            WHEN NOT r.people THEN 'move as dependency'
            ELSE 'retire candidate' END AS status,
       count(*) AS tables,
       string_agg(t.table_name, ', ' ORDER BY t.table_name) AS which
FROM tables t
LEFT JOIN r USING (table_name)
GROUP BY status
ORDER BY status
