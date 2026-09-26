# Memory leak and OOMKilled pods

Owner: service teams; Kubernetes platform for node issues.

## Symptoms

- `memory_percent` climbs in a sawtooth: grows until the pod restarts, then repeats.
- Kubernetes events show `OOMKilled` and the restart count increases.
- Latency spikes during garbage-collection pauses before each restart.

## Likely causes

- An unbounded in-memory cache or map (no max size, no TTL, no eviction).
- A new feature holding references to large objects per request.
- Memory limit set below the working set after traffic growth.

## Diagnosis

1. Confirm the sawtooth pattern on `memory_percent` over the last few hours.
2. Check recent deploys for new caches, buffers, or dependency upgrades.
3. Capture a heap dump from a pod before it is killed and look for the largest retained objects.

## Mitigation

1. Roll back the deploy that introduced the leak, or disable its feature flag.
2. As a stopgap, raise the memory limit and add replicas so restarts don't drop capacity.
3. Add a max size and TTL to any unbounded cache before re-deploying.

## Escalation

Page the Kubernetes platform team if OOMKills happen across many services on the same nodes.
