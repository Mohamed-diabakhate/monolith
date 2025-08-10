Keeper service to monitor and manage Aave positions on Arbitrum and Sonic.

Quick start:

1. Copy env

```bash
cp .env.sample .env
```

2. Fill RPCs, pool addresses, and monitored users

```bash
# .env
ARBITRUM_RPC=...
SONIC_RPC=...
ARBITRUM_AAVE_POOL=0x794a61358D6845594F94dc1DB02A252b5b4814aD
SONIC_AAVE_POOL=0x5362dBb1e601abF3a4c14c22ffEdA64042E5eAA3
USERS=0xYourEOA,0xAnother
INTERVAL_MS=60000
```

3. Install & run

```bash
npm i
npm run dev
```

The loop prints account health factor and warns when below threshold. Next steps:
- Add write adapters to repay/supply/withdraw with slippage controls.
- Integrate Odos/1inch for swaps.
- Add Safe submission for transactions.
- Alerting via webhook when actions are needed.
