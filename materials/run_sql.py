# Runs a setup .sql then queries separated by ";;" in DuckDB and prints each result. Usage: python3 -I materials/run_sql.py setup.sql queries.sql
import duckdb,sys
con=duckdb.connect()
con.execute(open(sys.argv[1]).read())
for i,q in enumerate(open(sys.argv[2]).read().split(';;')):
    q=q.strip()
    if not q: continue
    print('--- Q',i+1); print(con.sql(q))
