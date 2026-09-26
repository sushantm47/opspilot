# Database connection pool exhaustion

Owner: platform-data. Applies to all services using the shared Postgres cluster.

## Symptoms

- p99 latency jumps from ~200 ms to several seconds, followed by HTTP 5xx.
- Logs show "timeout acquiring connection" or "connection pool exhausted".
- `db_connections_in_use` sits at the configured pool maximum.

## Likely causes

- A deploy lowered `DB_POOL_SIZE` or raised the number of worker threads.
- A slow query or missing index holds connections longer than usual.
- A connection leak: a code path that doesn't return connections on error.

## Diagnosis

1. Compare `db_connections_in_use` with the pool size in the latest deploy config.
2. Check the most recent deploy diff for pool or thread-count changes.
3. Look for slow queries in the database dashboard (top queries by total time).

## Mitigation

1. If a deploy in the last few hours changed pool settings, roll back that deploy.
2. If no deploy is involved, temporarily raise the pool size within the database's max_connections budget.
3. Kill long-running idle-in-transaction sessions older than 5 minutes.

## Escalation

Page platform-data if connections stay saturated for 15 minutes after mitigation.
