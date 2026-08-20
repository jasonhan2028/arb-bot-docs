---
title: Failures & Recovery
sidebar_position: 9
---

# Failures & Recovery

This page records genuine execution mismatches separately from safe aborts. A safe PM zero-fill where Kalshi is never sent is **not** counted as a failure.

## Recovered live mismatch — United Kingdom vs Mexico

**Date:** 2026-08-20  
**Execution sequence:** PM-first  
**Direction:** Kalshi YES + PM NO  
**PM fill:** 1 contract  
**Kalshi fill:** 0 contracts  
**Final residual exposure:** 0 contracts  
**Recovery status:** Fully recovered on the first attempt  
**Estimated recovery P&L:** -$0.03

### What happened

The bot detected an executable arbitrage and sent the PM IOC first. PM filled the full one-contract position. Immediately before the Kalshi hedge, the Kalshi book still showed executable liquidity at the approved limit, but the subsequent Kalshi FOK was rejected for insufficient resting volume.

Post-error diagnostics showed that the Kalshi best ask had moved above the submitted limit by the time the order reached the exchange. The bot therefore held a confirmed one-sided PM position.

### Recovery

Automatic mismatch recovery activated immediately. The bot found executable PM liquidity within the configured maximum unwind-loss bound and sold the full unmatched contract on the first recovery attempt. The residual position was reduced to zero, after which the launcher stopped all workers for account-state safety.

### Engineering change

This incident exposed a weakness in using a Kalshi hedge limit calculated before the PM fill. The next worker version recalculates the maximum Kalshi hedge price from the **actual PM all-in fill cost** before sending the hedge. This allows the hedge limit to expand only when the realized PM fill creates additional profitable headroom, while preserving the minimum required arbitrage edge.

## Classification policy

| Classification | Meaning |
|---|---|
| ✅ Completed | Both legs filled as intended |
| 🟡 Safe abort | PM did not fill and Kalshi was never sent |
| 🟠 Mismatch — fully recovered | One leg filled, the hedge failed, and automatic recovery returned residual exposure to zero |
| 🔴 Mismatch — unresolved | Recovery failed or residual exposure remained |

The goal of this ledger is to make execution failures visible rather than hiding them inside aggregate success statistics. Each mismatch should document the failure mode, recovery outcome, and resulting engineering change.
