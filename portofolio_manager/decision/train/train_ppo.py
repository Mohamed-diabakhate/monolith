from __future__ import annotations

import os
import pandas as pd
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy

from decision.features.indicators import build_indicators
from decision.env.build_env import build_env
import argparse


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
    parser = argparse.ArgumentParser(description="Train PPO for capital rotation")
    parser.add_argument("--csv", type=str, default=None, help="Path to OHLCV CSV (defaults to data/btc_usdc.csv)")
    parser.add_argument("--timesteps", type=int, default=300_000, help="Total training timesteps")
    parser.add_argument("--window", type=int, default=64, help="Env window size")
    parser.add_argument("--fee", type=float, default=0.001, help="Exchange commission (fraction)")
    parser.add_argument("--alloc_levels", type=int, default=9, help="Discrete allocation levels (set 0 or 1 to use binary)")
    parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate")
    parser.add_argument("--batch_size", type=int, default=256, help="Batch size")
    parser.add_argument("--n_steps", type=int, default=2048, help="Rollout steps per update")
    parser.add_argument("--gamma", type=float, default=0.99, help="Discount factor")
    parser.add_argument("--gae_lambda", type=float, default=0.95, help="GAE lambda")
    parser.add_argument("--clip_range", type=float, default=0.2, help="PPO clip range")
    parser.add_argument("--ent_coef", type=float, default=0.0, help="Entropy coefficient")
    args = parser.parse_args()
    root = os.path.dirname(os.path.dirname(__file__))
    data_path = args.csv or os.path.join(root, "data", "btc_usdc.csv")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Expected data at: {data_path}")

    df = load_csv(data_path)
    df = build_indicators(df)

    split = int(len(df) * 0.7)
    train_df, test_df = df.iloc[:split], df.iloc[split:]

    env = build_env(train_df, fee=args.fee, window_size=args.window, allocation_levels=args.alloc_levels)
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        tensorboard_log=os.path.join(root, "runs", "ppo_rotation"),
        learning_rate=args.lr,
        batch_size=args.batch_size,
        n_steps=args.n_steps,
        gamma=args.gamma,
        gae_lambda=args.gae_lambda,
        clip_range=args.clip_range,
        ent_coef=args.ent_coef,
    )
    model.learn(total_timesteps=args.timesteps)

    # Evaluate
    test_env = build_env(test_df, fee=args.fee, window_size=args.window, allocation_levels=args.alloc_levels)
    mean_reward, std_reward = evaluate_policy(model, test_env, n_eval_episodes=3)
    print({"mean_reward": mean_reward, "std_reward": std_reward})

    # Save
    models_dir = os.path.join(root, "models")
    os.makedirs(models_dir, exist_ok=True)
    model.save(os.path.join(models_dir, "ppo_capital_rotation"))


if __name__ == "__main__":
    main()


