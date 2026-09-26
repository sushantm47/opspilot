# Disk full on a host or volume

Owner: service teams; infrastructure for shared volumes.

## Symptoms

- Writes fail with "No space left on device".
- `disk_used_percent` above 95% on the log or data volume.
- Service health checks fail because temp files cannot be created.

## Likely causes

- Log rotation stopped or a debug log level was left enabled.
- Large temporary files or core dumps accumulating.
- Data volume growth outpaced provisioning.

## Diagnosis

1. Find the largest directories on the full volume.
2. Check whether log level changed in a recent deploy or config push.
3. Verify the log-rotation job is running.

## Mitigation

1. Delete or compress rotated logs and core dumps to free space immediately.
2. Revert debug logging to INFO.
3. Expand the volume and add an alarm at 80% usage.

## Escalation

Page infrastructure if a shared volume is affected.
