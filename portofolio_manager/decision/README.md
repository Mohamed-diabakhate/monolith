## Capital Rotation Strategy (TensorTrade)

**Goal**: Rotate 100% of capital between `BTC` and `USDC` to maximize returns while controlling drawdowns, using an RL agent trained on OHLCV + indicators.

Framework: TensorTrade + Stable-Baselines3. See the upstream library: [TensorTrade repository](https://github.com/tensortrade-org/tensortrade).

### Quickstart

1. Install dependencies

```
pip install -r requirements.txt
```

2. Prepare data

- Place a CSV at `decision/data/btc_usdc.csv` with columns at minimum: `time,open,high,low,close,volume`.
- `time` should be parseable to a timestamp.
- Or fetch the last 1000 1h candles from Binance with the helper script:

  ```bash
  cd decision
  chmod +x fetch_btc_usdc.sh
  ./fetch_btc_usdc.sh
  ```

3. Fetch larger dataset (optional)

You can download a larger dataset directly from Binance using the paginator script. Examples:

```bash
cd decision
chmod +x fetch_btc_usdc.sh
# Hourly BTC/USDC from 2019 to now
SYMBOL=BTCUSDC INTERVAL=1h START="2019-01-01 00:00:00" ./fetch_btc_usdc.sh
# 4-hour BTC/USDT for the last few years
SYMBOL=BTCUSDT INTERVAL=4h START="2020-01-01" ./fetch_btc_usdc.sh
```

This writes `data/btc_usdc.csv` with columns: `time,open,high,low,close,volume`.

4. Train PPO agent

From the directory one level above `decision/` (so Python can find the `decision` package):

```
python3 -m decision.train.train_ppo
```

This will:

- Build indicators (RSI, EMAs, ATR, etc.)
- Construct a TensorTrade environment with a custom action scheme (0=all BTC, 1=all USDC) and a risk-adjusted reward
- Train PPO, save the model to `decision/models/`

5. Evaluate

The script runs a quick evaluation on a held-out time split and prints summary reward. TensorBoard logs (if enabled) are under `decision/runs/`.

### Post-training evaluation

From one level above `decision/` (i.e., `portofolio_manager/`):

```bash
python3 -m decision.train.eval_ppo
```

Artifacts will be written to `decision/reports/`:

- `eval_results.csv`: per-step `timestamp,step,action,net_worth`
- `equity_curve.png`: equity curve on the test split

If you see `ModuleNotFoundError: No module named 'decision'`, make sure you are running the command from the parent directory of `decision/`.

### Project layout

```
decision/
  ├─ data/
  │   └─ btc_usdc.csv            # your OHLCV data (not tracked)
  ├─ env/
  │   └─ build_env.py            # environment assembly
  ├─ features/
  │   └─ indicators.py           # indicator and feature building
  ├─ schemes/
  │   ├─ capital_rotation.py     # 2-action rotation scheme
  │   └─ reward.py               # risk-adjusted reward with switch penalty
  ├─ train/
  │   └─ train_ppo.py            # PPO training script
  ├─ README.md
  └─ requirements.txt
```

### Configuration knobs

- Exchange fee and slippage: set in `env/build_env.py`
- Reward penalties (volatility / switching): `schemes/reward.py`
- Window sizes, indicators: `features/indicators.py`

### Notes

- Prevent overtrading: non-zero commission configured on the exchange, plus switching penalty in reward.
- Avoid whipsaws: switching penalty and momentum/volatility features.
- Evaluate strategy: consider Sharpe, Sortino, Max Drawdown, turnover, number of switches.

Reference: [TensorTrade](https://github.com/tensortrade-org/tensortrade)
