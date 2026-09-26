# Postmortem: checkout-api outage from connection pool exhaustion (March 2026)

## Summary

For 47 minutes checkout-api returned HTTP 503 for 38% of requests. A config change in
deploy v2.9.0 lowered the database pool size from 20 to 5 while request concurrency
stayed the same, so requests queued waiting for connections and timed out.

## Timeline

- 14:02 deploy v2.9.0 reaches 100% of hosts.
- 14:09 p99 latency alarm fires; on-call starts investigating application logs.
- 14:31 on-call notices "timeout acquiring connection" in logs.
- 14:49 rollback to v2.8.3 completes; latency recovers within 2 minutes.

## Root cause

The pool size change was part of an unrelated refactor and was not called out in the
code review. There was no alarm on pool saturation, only on latency.

## What went well

Rollback was fast once the cause was found.

## What went wrong

It took 22 minutes to connect the latency alarm to the deploy.

## Action items

- Add an alarm on db_connections_in_use at 90% of pool size.
- Require explicit review for connection-pool config changes.
- Show recent deploys in the alarm description.
