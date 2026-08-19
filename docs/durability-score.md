---
title: Durability Score
sidebar_position: 6
---
# Durability score

Raw arbitrage edge is not enough. Many opportunities disappear faster than an order can reach the venues.

The current score has four binary components:

1. Kalshi top-depth change over 100 ms is nonnegative.
2. Kalshi best-price changes over 100 ms are at most one.
3. PM top-depth concentration is at least 90%.
4. The modeled edge remains nonnegative if the current Kalshi top level disappears.

A score of **3 or 4** is required. At least 100 ms of Kalshi history must exist before the score is considered ready.

## Prospective survival analysis

The v14 overnight sample contained 112 logged opportunities. Survival means the original submitted limits remained fillable and the modeled edge remained at least one cent.

![Durability survival curve](/img/durability_survival_curve.png)

The score improved selection at short horizons but did not make opportunities immune to PM-side changes. That finding motivated later revalidation and PM-first execution.

The score is therefore a **selection feature**, not a substitute for fresh exchange timestamps, exact-limit depth, immediate revalidation, or fail-closed sequencing.

