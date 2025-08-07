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

3. Train PPO agent

From the directory one level above `decision/` (so Python can find the `decision` package):

```
python3 -m decision.train.train_ppo
```

This will:

- Build indicators (RSI, EMAs, ATR, etc.)
- Construct a TensorTrade environment with a custom action scheme (0=all BTC, 1=all USDC) and a risk-adjusted reward
- Train PPO, save the model to `decision/models/`

4. Evaluate

The script runs a quick evaluation on a held-out time split and prints summary reward. TensorBoard logs (if enabled) are under `decision/runs/`.

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
