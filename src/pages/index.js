import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';

export default function Home() {
  return (
    <Layout title="Cross-Exchange Sports Arbitrage" description="Engineering documentation for a Polymarket US × Kalshi arbitrage system">
      <header className="hero hero--primary">
        <div className="container">
          <h1 className="hero__title">Cross-Exchange Sports Arbitrage</h1>
          <p className="hero__subtitle">
            From raw price detection to multi-market, PM-first live execution.
          </p>
          <Link className="button button--secondary button--lg" to="/docs/overview">
            Read the documentation
          </Link>
        </div>
      </header>
      <main className="container margin-vert--lg">
        <div className="metricGrid">
          <div className="metricCard"><div className="metricValue">3</div><div className="metricLabel">consecutive v15 completed arbs</div></div>
          <div className="metricCard"><div className="metricValue">PM-first</div><div className="metricLabel">current execution sequence</div></div>
          <div className="metricCard"><div className="metricValue">4 features</div><div className="metricLabel">durability score</div></div>
          <div className="metricCard"><div className="metricValue">10</div><div className="metricLabel">markets in latest live canary</div></div>
        </div>
        <h2>What this site captures</h2>
        <p>
          Architecture, market matching, execution filters, latency work, exchange-timestamp freshness,
          durability research, mismatch recovery, live outcomes, and the reasoning behind each major version.
        </p>
      </main>
    </Layout>
  );
}
