<!-- learn-with-phoebe hub banner -->
> ### 📚 Part of [**Learn with Phoebe**](https://phoebefu6.github.io/learn-with-phoebe/)
> The shelf of 206 free, hands-on courses on AI, data, and the craft around them. **[Browse every course ↗](https://phoebefu6.github.io/learn-with-phoebe/)**
<!-- /learn-with-phoebe hub banner -->

# Ship It: Data Platform Migration

Move a warehouse without breaking the numbers. Sixteen 45-minute sessions in two tracks, by Phoebe Fu.

- **Leader track (6 sessions, no code):** why migrations break the numbers, inventory before plan, lift, rebuild or retire, the parity bar, cutover day and the rollback, the week after and switching off.
- **Builder track (10 sessions, SQL in DuckDB and the browser):** inventory from the query log, the dependency graph, translating the SQL, row and key parity, aggregate parity, historical reload, parallel run, cutover rehearsal and rollback, the drift that hides, and the parity bench.

The running case, Serai Commerce, is constructed. Its orders are real: 8,614 delivered orders derived and masked from the Brazilian E-Commerce Public Dataset by Olist (Kaggle, CC BY-NC-SA 4.0); no review text is used. The parity bench in Builder session 10 plants seven constructed drifts in a second copy of those orders and scores five rungs of checks live in the browser. An independent Python reference (`materials/spm_reference.py`) matches the browser engine on every number of the ladder (`python3 -I materials/compare-ladder.py`).

Open `index.html` to start. Static HTML, no build step.
