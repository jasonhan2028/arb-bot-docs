---
title: Changelog
sidebar_position: 10
---
# Changelog

## Worker v15
- PM-first confirm-then-Kalshi execution.
- Kalshi preparation removed from the PM critical path.
- Post-PM-preparation revalidation.
- Pre-Kalshi-send hedge revalidation.
- Improved recovery-attempt logging.
- Execution stats schema 13.

## Worker v14
- Four-feature durability score became the primary durability gate.
- Legacy quote-age and extra-PM-tick rules retained as telemetry rather than hard blockers.

## Worker v13
- Bounded automatic mismatch recovery.
- Same-exchange unwind of only confirmed excess.
- Fail-closed behavior for unknown fill state.

## Worker v12
- PM exchange-timestamp freshness gate.
- Freshness-aware durability history.
- Stale-book reconnect watchdog.

## Worker v11
- Expanded PM order verification.
- Explicit automatic-order indicator.
- Terminal-state diagnostics for zero fills.

## Launcher v8
- Successful completed arbs are surfaced as `MULTI ARB COMPLETE`.
- Mismatch stops are classified separately.
- Execution CSV can serve as the authoritative fallback when final worker stdout is missing.

## Earlier multi-market versions
- Automatic sports discovery and participant matching.
- Process-per-market isolation.
- READY-state launcher lifecycle.
- Near-miss logging.
- Run IDs for exact experiment isolation.
