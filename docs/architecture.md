---
title: Architecture
sidebar_position: 2
---
# Architecture

## Control plane

The launcher periodically discovers compatible sports markets and runs one isolated worker process per matched game or match. The isolation keeps execution failures contained while allowing the launcher to stop all workers when account state may need inspection.

```text
Discovery / matching
      ↓
markets.auto.json
      ↓
multi-market launcher
      ↓
┌────────────┬────────────┬────────────┐
│ worker A   │ worker B   │ worker C   │
│ PM + Kal   │ PM + Kal   │ PM + Kal   │
│ books      │ books      │ books      │
└────────────┴────────────┴────────────┘
```

## Data plane

Each worker maintains:
- Polymarket US book state with local receive time and exchange `transactTime`.
- Kalshi full-book WebSocket state.
- Short rolling book history for 50/100/250 ms durability features.
- Cumulative depth inside the exact submitted limits.

## Execution plane

The current worker is **PM-first**:
1. Validate the opportunity.
2. Prepare the PM request.
3. Revalidate immediately after preparation.
4. Send PM IOC.
5. Start Kalshi preparation after the PM send point.
6. Wait for PM terminal state.
7. If PM fills zero, never send Kalshi.
8. If PM fills fully, revalidate the Kalshi hedge and send FOK.
9. If a confirmed mismatch remains, attempt bounded same-exchange recovery and stop.

This sequencing was introduced after repeated `PM=0 / Kalshi=1` live mismatches under concurrent order release.
