const config = {
  title: 'Cross-Exchange Sports Arbitrage',
  tagline: 'Engineering notes, execution research, and live validation',
  url: 'https://jasonhan2028.github.io',
  baseUrl: '/arb-bot-docs/',
  organizationName: 'jasonhan2028',
  projectName: 'arb-bot-docs',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          routeBasePath: 'docs',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
  themeConfig: {
    navbar: {
      title: 'Arb Bot Docs',
      items: [
        {to: '/docs/overview', label: 'Documentation', position: 'left'},
        {to: '/docs/live-executions', label: 'Live Results', position: 'left'},
        {to: '/docs/development-history', label: 'Timeline', position: 'left'}
      ],
    },
    footer: {
      style: 'dark',
      links: [],
      copyright: `Research documentation. Generated ${new Date().getFullYear()}.`,
    },
  },
};

module.exports = config;
