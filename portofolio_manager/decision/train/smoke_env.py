from __future__ import annotations

import os
import pandas as pd
import numpy as np

from decision.features.indicators import build_indicators
from decision.env.build_env import build_env


def main():
    root = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(root, "data", "btc_usdc.csv")
    if not os.path.exists(data_path):
        # Create a tiny synthetic dataset for smoke testing
        dates = pd.date_range("2021-01-01", periods=300, freq="D")
        price = np.cumprod(1 + 0.001 * (np.random.randn(len(dates)))) * 30000
        df = pd.DataFrame({
            "time": dates,
            "open": price,
            "high": price * 1.01,
            "low": price * 0.99,
            "close": price,
            "volume": 1000,
        })
    else:
        df = pd.read_csv(data_path)
    df["time"] = pd.to_datetime(df["time"])  # type: ignore[arg-type]
    df = df.set_index("time")
    df = build_indicators(df)

    env = build_env(df.iloc[-200:])
    obs = env.reset()
    done = False
    steps = 0
    total_reward = 0.0
    while not done and steps < 50:
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
        total_reward += float(reward)
        steps += 1
    print({"steps": steps, "total_reward": total_reward})


if __name__ == "__main__":
    main()


