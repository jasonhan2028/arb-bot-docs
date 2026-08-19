# Arb Bot Documentation Site

Repo-ready Docusaurus documentation for the Polymarket US × Kalshi sports arbitrage project.

## Included

- architecture and execution-flow documentation
- chronological development history
- discovery and safety filters
- latency-engineering write-up
- durability-score methodology
- PM exchange freshness and mismatch recovery
- sanitized live execution ledger
- generated charts
- GitHub Pages deployment workflow

## Run locally

Requires Node.js 20+.

```bash
npm install
npm start
```

## Build

```bash
npm run build
```

## Publish with GitHub Pages

1. Create a GitHub repository named `arb-bot-docs`.
2. Replace `YOUR_GITHUB_USERNAME` in `docusaurus.config.js`.
3. Push this project to the `main` branch.
4. In repository Settings → Pages, use **GitHub Actions** as the source.
5. Push again or manually run the included workflow.

## Updating metrics

Keep raw exports outside the public repo, then run:

```bash
python scripts/build_metrics.py /path/to/exported_csv_directory
```

Commit only sanitized aggregates and figures. Never commit credentials, private keys,
`market.env`, server details, or unsanitized account/order metadata.

## Next iteration

- automatically regenerate charts from each export
- add an experiment/version registry
- add per-version latency tables
- add a richer execution funnel
- add a private/raw-data companion workflow if desired
