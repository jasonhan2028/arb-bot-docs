---
title: Latency Engineering
sidebar_position: 5
---
# Latency engineering

Latency work focuses on the interval between opportunity detection and the first irreversible order action.

## Why the PM critical path mattered

The historical concurrent design prepared both venue requests before releasing either send. A slow preparation path on one venue could therefore delay the other.

The third live mismatch showed that the PM quote could disappear during that local preparation window.

## PM-first redesign

```text
detect
→ validate
→ prepare PM
→ revalidate
→ PM HTTP send
→ begin Kalshi preparation
→ PM response
→ revalidate Kalshi
→ Kalshi HTTP send
```

This removes Kalshi preparation from the PM critical path.

![PM critical-path latency](/arb-bot-docs/img/pm_send_latency.png)

## Logged latency stages

Execution rows capture detection → execute start, initial book read, limit calculation, final depth analysis, PM preparation, post-PM-preparation revalidation, detection → PM send, PM send → Kalshi preparation start, Kalshi preparation, PM HTTP round trip, PM response → Kalshi send, and Kalshi HTTP round trip.

That makes latency regressions attributable to an exact stage.
