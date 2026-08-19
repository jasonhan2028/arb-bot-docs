---
title: Data & Methodology
sidebar_position: 9
---
# Data and methodology

## Data products

The worker writes three primary CSV families.

### Execution statistics
One row per execution decision or live attempt. Includes filters, limits, fill states, order-state diagnostics, latency stages and recovery fields.

### Opportunity statistics
Tracks qualifying opportunities forward in time to measure whether original limits and edge survive at 25, 50, 100, 250, 500 and 1000 ms horizons.

### Near-miss statistics
Captures opportunities close to the execution threshold so future modeling is not trained only on obvious winners.

## Recent executable depth

For sizing analysis, the useful depth metric is:

```text
min(PM cumulative depth inside profitable limit,
    Kalshi cumulative depth inside profitable limit)
```

![Recent depth availability](/arb-bot-docs/img/depth_availability.png)

Displayed depth is not treated as guaranteed future fill. The live strategy revalidates before each order decision.

## Reproducibility and privacy

The repository includes a starter `scripts/build_metrics.py` that reads exported CSVs and produces sanitized summary JSON.

Raw credentials, private keys, server addresses, and unsanitized account/order metadata should never be committed to the public site repository.
