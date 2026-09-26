# Postmortem: search-service OOMKilled restart loop (May 2026)

## Summary

search-service pods were OOMKilled roughly every 25 minutes for 3 hours, degrading
search latency. Deploy v5.2.0 added an in-process result cache with no size limit.

## Root cause

The cache stored full result pages keyed by raw query string, so memory grew with every
unique query until the container hit its limit.

## Action items

- All in-process caches must set a max size and TTL (lint rule added).
- Add a memory growth-rate alarm, not only a threshold alarm.
