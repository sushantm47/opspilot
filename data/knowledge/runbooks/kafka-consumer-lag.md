# Kafka consumer lag growing

Owner: streaming-platform.

## Symptoms

- `consumer_lag` for a consumer group rises steadily instead of oscillating.
- Downstream work (payments settlement, notifications) is delayed.
- Logs show frequent "rebalancing" or "max.poll.interval.ms exceeded".

## Likely causes

- Processing per message got slower (new external call, larger payloads).
- Consumers are kicked out of the group because a poll loop exceeds max.poll.interval.ms, causing rebalance storms.
- Too few partitions or consumers for the current throughput.

## Diagnosis

1. Check whether lag grows on all partitions (throughput problem) or a few (hot partition or stuck consumer).
2. Search logs for rebalance and poll-interval errors.
3. Check recent deploys for changes in batch size or processing logic.

## Mitigation

1. If rebalances are looping, lower max.poll.records or raise max.poll.interval.ms so each poll finishes in time.
2. Scale consumers up to the partition count.
3. Roll back a recent deploy that slowed message processing.

## Escalation

Page streaming-platform if lag exceeds 30 minutes of traffic.
