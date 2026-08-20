---
title: Failures & Recovery
sidebar_position: 9
---

# Failures & Recovery

This ledger contains genuine one-sided execution incidents. Safe PM zero-fill aborts are excluded.

## Incident ledger

| Date | Market | Direction | Fills (PM / Kalshi) | Failure | Recovery | Residual | Recovery P&L |
|---|---|---|---:|---|---|---:|---:|
| 2026-08-20 | United Kingdom vs Mexico | Kalshi YES + PM NO | 1 / 0 | Kalshi FOK insufficient resting volume | Fully recovered | 0 | -$0.03 |

**Recorded mismatches:** 1 · **Fully recovered:** 1 · **Unresolved:** 0

## Classification

| Classification | Meaning |
|---|---|
| ✅ Completed | Both legs filled as intended |
| 🟡 Safe abort | PM did not fill and Kalshi was never sent; not included in this ledger |
| 🟠 Fully recovered mismatch | One leg filled, hedge failed, and automatic recovery reduced residual exposure to zero |
| 🔴 Unresolved mismatch | Recovery failed or residual exposure remained |

New mismatch rows are added automatically when uploaded execution CSVs or ZIP exports contain a mismatch status.
