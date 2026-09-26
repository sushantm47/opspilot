# Postmortem: payments-worker consumer rebalance storm (July 2026)

## Summary

Settlement was delayed by up to 40 minutes. A new fraud-check call added ~400 ms per
message, so polling a batch of 500 records exceeded max.poll.interval.ms. Consumers were
removed from the group and rejoined in a loop.

## Root cause

Batch size was tuned for the old per-message latency and was not revisited when the
fraud-check call was added.

## Action items

- Alarm on rebalance rate, not just lag.
- Load-test consumers when per-message processing time changes.
