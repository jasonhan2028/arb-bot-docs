---
title: Freshness & Recovery
sidebar_position: 7
---
# Exchange freshness and mismatch recovery

## Two notions of freshness

The worker tracks:
- **local receive age** — how long ago this process received the update;
- **PM exchange book age** — how old the exchange-generated timestamp actually is.

A reconnect can make stale data look locally new, so local receive age alone is insufficient.

The current worker applies a hard PM exchange-age ceiling before submission and excludes stale snapshots from durability history.

## Mismatch recovery

If both fill quantities are known and one venue has confirmed excess exposure, the worker attempts to close only the excess on the same venue.

Recovery is bounded by maximum permitted loss per contract, maximum attempts, retry delay, and fail-closed handling for unknown order state.

Per-attempt recovery logging records the observed BBO, recovery limit/floor, whether the BBO crossed the permitted floor, requested quantity, fill quantity, residual quantity, order IDs, and errors.

The bot stops after a mismatch whether recovery succeeds or fails.

