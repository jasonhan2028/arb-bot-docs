---
title: Development History
sidebar_position: 3
---
# Development history

The system's changes are best understood as responses to observed failure modes.

## Phase 1 — Basic execution

The first implementation detected complementary outcomes and attempted to buy both sides when the combined price implied a positive edge.

Early safeguards added fee-aware profitability, tick rounding, IOC/FOK semantics, cumulative depth rather than top-of-book size alone, and strict market-side mapping.

## Phase 2 — Multi-market discovery

The bot moved from hand-selected markets to automatic discovery and matching across compatible sports. Matching became deliberately conservative through participant identity checks, time compatibility, ambiguity thresholds, and explicit exclusion of props and non-binary structures.

## Phase 3 — Durability telemetry

Rolling 50/100/250 ms book history was added to answer a different question from raw edge:

> Is this opportunity likely to survive long enough to execute?

## Phase 4 — Live mismatch diagnostics

Three live mismatches shaped the architecture.

### Mismatch #1
Observed `PM=0 / Kalshi=1`. PM terminal-state diagnostics and request payload handling were strengthened.

### Mismatch #2 — stale exchange state
A PM snapshot appeared locally recent but carried a much older exchange timestamp.

**Change:** PM exchange-side book age became a hard execution gate.

### Mismatch #3 — preparation latency
At detection, PM liquidity existed inside the submitted limit, but a Kalshi request-preparation spike delayed the actual PM send while the PM opportunity disappeared.

**Change:** PM-first execution plus post-preparation revalidation.

![PM send latency](/img/pm_send_latency.png)

## Phase 5 — PM-first execution

The current design sends PM first, confirms the PM terminal state, and only then sends the Kalshi hedge if it remains executable.

The first three confirmed two-leg PM-first executions were all successful.

