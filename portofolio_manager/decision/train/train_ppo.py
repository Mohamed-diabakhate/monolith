from __future__ import annotations

import os
import pandas as pd
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy

from decision.features.indicators import build_indicators
from decision.env.build_env import build_env


def load_csv(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # Basic schema expectations
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])  # type: ignore[arg-type]
        df = df.set_index("time")
    needed = {"open", "high", "low", "close", "volume"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")
    return df


def main():
    root = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(root, "data", "btc_usdc.csv")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Expected data at: {data_path}")

    df = load_csv(data_path)
    df = build_indicators(df)

    split = int(len(df) * 0.7)
    train_df, test_df = df.iloc[:split], df.iloc[split:]

    env = build_env(train_df)
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=os.path.join(root, "runs", "ppo_rotation"))
    model.learn(total_timesteps=300_000)

    # Evaluate
    test_env = build_env(test_df)
    mean_reward, std_reward = evaluate_policy(model, test_env, n_eval_episodes=3)
    print({"mean_reward": mean_reward, "std_reward": std_reward})

    # Save
    models_dir = os.path.join(root, "models")
    os.makedirs(models_dir, exist_ok=True)
    model.save(os.path.join(models_dir, "ppo_capital_rotation"))


if __name__ == "__main__":
    main()


