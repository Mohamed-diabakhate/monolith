Crypto Portfolio Dashboard (Next.js)

## Overview

Modern, Aave-inspired dashboard to view multi-chain balances and Aave positions. Includes a demo mode with synthetic data so you can try the UI without API keys.

UI inspiration: [Aave App](https://app.aave.com/)

Default address used in the demo: `0x200b0E0b2030c4F9fba3312C3C7505b9050aaFD6`

## Features

- Multi-chain balances via ANKR Token API (proxied through `/api/balances`)
- USD pricing via Binance (USDT pairs) with ANKR price fallback
- Portfolio summary (Total, BTC vs Alts) and pie chart
- Aave v3 positions (Polygon, Arbitrum, Optimism, Avalanche) via The Graph
- Clean UI with sidebar, stat cards, glass cards, and responsive layout

## Quickstart

Start the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open http://localhost:3000

Then click "Load demo data" to populate the dashboard using mocks.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Configuration

Create `.env.local` in the `web/` folder:

ANKR_API_KEY=your_ankr_key

If absent, the app will use the public `https://rpc.ankr.com/multichain` (rate limited).

## Demo mode (synthetic data)

- Balances: `/api/balances?address=<addr>&chains=eth,polygon,arbitrum&mock=1`
- Aave positions: `/api/aave?address=<addr>&chain=polygon-mainnet&mock=1`

In the main page, the "Load demo data" button requests with `mock=1` automatically.

## Tech stack

- Next.js App Router + TypeScript
- Tailwind (via the v3 preset) and Geist font
- Recharts for charts

## Scripts

- `npm run dev` — start dev server
- `npm run build` — production build
- `npm start` — start production server

## API routes

- `GET /api/balances` — proxy to ANKR Token API (supports `address`, `chains`, `mock=1`)
- `GET /api/aave` — fetch Aave v3 positions via The Graph (supports `address`, `chain`, `mock=1`)

## Deployment

Deployable on Vercel or any Node.js host.

See Next.js docs for more details.
