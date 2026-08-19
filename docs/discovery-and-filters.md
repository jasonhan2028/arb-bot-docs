---
title: Discovery & Filters
sidebar_position: 4
---
# Discovery and execution filters

## Compatible markets

The discovery system is designed around binary markets whose economic outcome can be mapped cleanly across both exchanges.

Accepted categories include full-game/full-match winners for baseball, basketball, football, hockey, tennis, cricket, esports and fight winner markets, plus soccer “to advance” structures when the mapping is unambiguous.

Explicitly excluded structures include spreads, totals, periods, sets, game totals, player props, and ambiguous three-way full-time soccer winner markets.

## Matching

Markets are matched using normalized participant names, abbreviations/acronyms, token and surname matching, start-time compatibility, and ambiguity margins. Ambiguous pairs are reviewed rather than launched automatically.

## Hard pre-trade filters

An opportunity must survive:
1. valid mapping,
2. valid live WebSocket state,
3. PM exchange timestamp freshness,
4. fee-inclusive edge,
5. profitability at exact submitted limits,
6. cumulative depth cushion at both venues,
7. durability-history readiness,
8. durability score threshold,
9. post-PM-preparation revalidation.

The filters are treated as **execution safety**, not merely signal selection.
