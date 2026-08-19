---
title: Live Executions
sidebar_position: 8
---
# Live execution ledger

## PM-first era

| Outcome | Market | Direction | Quantity | Conservative realized edge |
|---|---|---|---:|---:|
| ✅ Completed | FUSION X / No Sweat Blossom | Kalshi YES + PM NO | 1 + 1 | +2.76¢ |
| ✅ Completed | Jamaica Kingsmen / St. Kitts and Nevis Patriots | PM YES + Kalshi NO | 1 + 1 | +2.15¢ |
| ✅ Completed | Kalyakina / Lu vs Tian Deng / HAN | Kalshi YES + PM NO | 1 + 1 | +2.26¢ |

The latest completion was explicitly classified by launcher v8 as `status=both_filled`, with one contract filled on each venue and a conservative realized edge of `0.0226`.

## Safe aborts

Under PM-first execution, a verified PM zero fill causes the Kalshi order to remain unsent. These rows are logged as:

```text
pm_no_fill_kalshi_not_sent
```

They are not counted as failed arbitrages because the second venue was never exposed.

## Historical failures

Before PM-first execution, three live mismatches were observed with the high-level pattern:

```text
PM filled 0
Kalshi filled 1
```

Those failures led to PM order verification, exchange-timestamp freshness, automatic recovery, PM-first execution and post-preparation revalidation.

![Execution outcomes](/arb-bot-docs/img/live_execution_outcomes.png)
