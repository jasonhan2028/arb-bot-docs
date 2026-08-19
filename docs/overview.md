---
title: Overview
sidebar_position: 1
---
# Project overview

This project is a low-latency sports arbitrage system that identifies economically equivalent binary outcomes on **Polymarket US** and **Kalshi**, checks whether the combined acquisition cost remains below the guaranteed $1 settlement value after fees, and attempts to execute a hedged position.

The system evolved from a single-market scanner into a multi-market architecture with conservative market matching, full-book WebSocket state, fee-aware depth analysis, durability scoring, exchange-timestamp freshness checks, automatic mismatch recovery, and a **PM-first confirm-then-hedge execution sequence**.

## Current live execution model

```text
discover compatible market
        ↓
match participants and start time
        ↓
maintain PM + Kalshi books
        ↓
fee-aware edge and cumulative-depth checks
        ↓
PM exchange-timestamp freshness
        ↓
four-feature durability score
        ↓
prepare PM request
        ↓
revalidate books and score
        ↓
send PM IOC
        ↓
PM full fill?
  ┌─────┴─────┐
  no          yes
  ↓            ↓
safe abort   prepare/revalidate Kalshi
Kalshi       ↓
not sent     send Kalshi FOK
             ↓
           both filled
```

The most important current design principle is that **a PM zero fill is a safe abort, not a failed arb**, because the Kalshi hedge is never transmitted unless PM first confirms the requested fill.

## Current validation

The PM-first design has produced three consecutive confirmed two-leg executions at one contract. Historical mismatches occurred before this design and directly drove the current execution architecture.

![Live execution outcomes](/img/live_execution_outcomes.png)

