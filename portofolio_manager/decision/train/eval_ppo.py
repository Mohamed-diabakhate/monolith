from __future__ import annotations

import os
import glob
import math
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from stable_baselines3 import PPO

from decision.features.indicators import build_indicators
from decision.env.build_env import build_env


@dataclass
class EvalRecord:
    timestamp: Optional[pd.Timestamp]
    step: int
    action: int
    net_worth: float


def load_csv(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])  # type: ignore[arg-type]
        df = df.set_index("time")
    required = {"open", "high", "low", "close", "volume"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")
    return df


def find_model_path(models_dir: str) -> str:
    # Prefer explicitly saved name, otherwise fallback to newest .zip
    explicit = os.path.join(models_dir, "ppo_capital_rotation.zip")
    if os.path.exists(explicit):
        return explicit
    zips = sorted(glob.glob(os.path.join(models_dir, "*.zip")), key=os.path.getmtime, reverse=True)
    if not zips:
        raise FileNotFoundError(f"No model .zip found in {models_dir}")
    return zips[0]


def compute_drawdown(equity: np.ndarray) -> float:
    running_max = np.maximum.accumulate(equity)
    drawdowns = (equity - running_max) / (running_max + 1e-12)
    return float(drawdowns.min())


def compute_sharpe(returns: np.ndarray, scale: float = 1.0) -> float:
    # returns are per-step; scale can be sqrt(steps_per_period). For hourly data ~ sqrt(24*365) if annualizing.
    mu = returns.mean()
    sigma = returns.std()
    if sigma < 1e-12:
        return 0.0
    return float((mu / sigma) * scale)


def evaluate_model(models_dir: str, data_path: str, window_size: int = 64) -> dict:
    root = os.path.dirname(os.path.dirname(__file__))

    df = load_csv(data_path)
    df = build_indicators(df)
    split = int(len(df) * 0.7)
    test_df = df.iloc[split:]

    env = build_env(test_df, window_size=window_size)

    model_path = find_model_path(models_dir)
    model = PPO.load(model_path)

    obs = env.reset()
    done = False
    records: List[EvalRecord] = []

    step_idx = 0
    # Align timestamps approximately with the rolling window offset
    timestamps = list(test_df.index)
    time_offset = min(window_size, max(0, len(timestamps) - 1))

    last_action: Optional[int] = None
    num_switches = 0

    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(int(action))
        if last_action is not None and int(action) != last_action:
            num_switches += 1
        last_action = int(action)

        ts: Optional[pd.Timestamp]
        mapped_idx = step_idx + time_offset
        if 0 <= mapped_idx < len(timestamps):
            ts = pd.Timestamp(timestamps[mapped_idx])
        else:
            ts = None

        net_worth = float(info.get("net_worth", np.nan))
        records.append(EvalRecord(timestamp=ts, step=step_idx, action=int(action), net_worth=net_worth))
        step_idx += 1

        # Avoid infinite loops in case of misconfigured env
        if step_idx > len(test_df) + 5 * window_size:
            break

    # Build DataFrame
    out = pd.DataFrame([{ 
        "timestamp": r.timestamp, 
        "step": r.step, 
        "action": r.action, 
        "net_worth": r.net_worth 
    } for r in records])

    # Metrics
    equity = out["net_worth"].replace([np.inf, -np.inf], np.nan).dropna().to_numpy()
    if equity.size < 2:
        raise RuntimeError("Not enough steps recorded during evaluation.")
    returns = np.diff(equity) / (equity[:-1] + 1e-12)
    total_return = float((equity[-1] / equity[0]) - 1.0)
    max_dd = compute_drawdown(equity)
    # Assuming hourly data; annualize roughly
    sharpe = compute_sharpe(returns, scale=math.sqrt(24 * 365))

    # Save artifacts
    reports_dir = os.path.join(root, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    csv_path = os.path.join(reports_dir, "eval_results.csv")
    out.to_csv(csv_path, index=False)

    # Plot equity curve with OHLC price overlay (normalized to start at equity start)
    fig, ax = plt.subplots(figsize=(11, 5))

    # X-axis selection
    use_time_axis = out["timestamp"].notna().any()
    if use_time_axis:
        x_equity = out["timestamp"]
    else:
        x_equity = out["step"]

    equity_series = out["net_worth"].replace([np.inf, -np.inf], np.nan).dropna()
    ax.plot(x_equity.iloc[: len(equity_series)], equity_series.values, label="Equity", color="#1f77b4", linewidth=1.6)

    # Build aligned price slice corresponding to env steps (skip initial window)
    price_slice = test_df.iloc[time_offset : time_offset + len(out)]
    # Align lengths defensively
    aligned_len = min(len(price_slice), len(x_equity))
    price_slice = price_slice.iloc[:aligned_len]
    x_price = (price_slice.index if use_time_axis else np.arange(aligned_len))

    # Prepare containers for dashboard/time-series export
    c_norm = None
    o_norm = h_norm = l_norm = None
    if aligned_len > 1 and {"open", "high", "low", "close"}.issubset(price_slice.columns):
        # Normalize OHLC to equity scale so curves overlay intuitively
        start_equity = float(equity_series.iloc[0]) if len(equity_series) > 0 else float(out["net_worth"].iloc[0])
        denom = float(price_slice["close"].iloc[0]) if float(price_slice["close"].iloc[0]) != 0 else 1.0
        scale = start_equity / denom
        o_norm = price_slice["open"].astype(float) * scale
        h_norm = price_slice["high"].astype(float) * scale
        l_norm = price_slice["low"].astype(float) * scale
        c_norm = price_slice["close"].astype(float) * scale

        # High-Low band
        ax.fill_between(x_price, l_norm.values, h_norm.values, color="#999999", alpha=0.15, label="Price High-Low (norm)")
        # Close line
        ax.plot(x_price, c_norm.values, color="#2ca02c", linewidth=1.0, alpha=0.9, label="Price Close (norm)")

    ax.set_title("Equity Curve with OHLC Overlay (Test)")
    ax.set_xlabel("Time" if use_time_axis else "Step")
    ax.set_ylabel("Net Worth / Normalized Price")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    png_path = os.path.join(reports_dir, "equity_curve.png")
    fig.savefig(png_path, dpi=150)
    plt.close(fig)

    # Build enriched time-series (aligned window)
    dash_len = min(len(equity_series), aligned_len if c_norm is not None else len(equity_series))
    eq_vals = np.asarray(equity_series.values[:dash_len], dtype=float)
    if use_time_axis:
        x_index = pd.to_datetime(x_equity.iloc[:dash_len].values)
    else:
        x_index = pd.Index(np.asarray(x_equity.iloc[:dash_len].values), name="step")

    df_ts = pd.DataFrame(index=x_index)
    df_ts["equity"] = eq_vals
    df_ts["returns"] = df_ts["equity"].pct_change().fillna(0.0)
    # Drawdown series
    run_max = np.maximum.accumulate(df_ts["equity"].values)
    df_ts["drawdown"] = (df_ts["equity"].values - run_max) / (run_max + 1e-12)

    if c_norm is not None:
        # Use normalized close aligned to equity
        df_ts["price_norm_close"] = np.asarray(c_norm.values[:dash_len], dtype=float)
        df_ts["alpha"] = df_ts["equity"] / (df_ts["price_norm_close"] + 1e-12)
    else:
        df_ts["price_norm_close"] = np.nan
        df_ts["alpha"] = np.nan

    # Approximate allocation from actions
    levels = getattr(env.action_scheme.action_space, "n", 2)
    actions_aligned = out["action"].iloc[:dash_len].to_numpy()
    if levels > 2:
        alloc = actions_aligned.astype(float) / float(max(1, levels - 1))
    else:
        alloc = (actions_aligned == 1).astype(float)
    df_ts["alloc_btc"] = alloc
    df_ts["turnover"] = np.concatenate([[0.0], np.abs(np.diff(alloc))])

    # Rolling metrics
    roll_window = 168  # ~ 1 week of hourly bars
    r = df_ts["returns"]
    mu = r.rolling(roll_window).mean()
    sigma = r.rolling(roll_window).std().replace(0.0, np.nan)
    downside = r.where(r < 0.0, 0.0)
    downside_sigma = downside.rolling(roll_window).std().replace(0.0, np.nan)
    df_ts["rolling_sharpe"] = (mu / sigma).fillna(0.0)
    df_ts["rolling_sortino"] = (mu / (downside_sigma + 1e-12)).fillna(0.0)

    # Export enriched CSV
    ts_csv_path = os.path.join(reports_dir, "eval_timeseries.csv")
    df_ts.reset_index().rename(columns={df_ts.index.name or "index": "timestamp"}).to_csv(ts_csv_path, index=False)

    # Dashboard plot
    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    # 1) Equity vs normalized close
    axes[0].plot(df_ts.index, df_ts["equity"], label="Equity", color="#1f77b4", linewidth=1.5)
    if c_norm is not None:
        axes[0].plot(df_ts.index, df_ts["price_norm_close"], label="Price Close (norm)", color="#2ca02c", linewidth=1.0, alpha=0.9)
    axes[0].set_ylabel("Equity / Price (norm)")
    axes[0].legend(loc="best")
    axes[0].grid(alpha=0.3)

    # 2) Drawdown
    axes[1].plot(df_ts.index, df_ts["drawdown"], color="#d62728", linewidth=1.0)
    axes[1].set_ylabel("Drawdown")
    axes[1].grid(alpha=0.3)

    # 3) Rolling Sharpe / Sortino
    axes[2].plot(df_ts.index, df_ts["rolling_sharpe"], label="Rolling Sharpe", color="#9467bd", linewidth=1.0)
    axes[2].plot(df_ts.index, df_ts["rolling_sortino"], label="Rolling Sortino", color="#8c564b", linewidth=1.0)
    axes[2].axhline(0.0, color="#999999", linewidth=0.8, linestyle="--")
    axes[2].set_ylabel("Risk-Adj")
    axes[2].legend(loc="best")
    axes[2].grid(alpha=0.3)

    # 4) Allocation and turnover bars
    axes[3].plot(df_ts.index, df_ts["alloc_btc"], label="Alloc BTC", color="#17becf", linewidth=1.0)
    axes[3].bar(df_ts.index, df_ts["turnover"], label="Turnover", color="#7f7f7f", width=1.0, alpha=0.3)
    axes[3].set_ylabel("Alloc / Turnover")
    axes[3].grid(alpha=0.3)
    axes[3].legend(loc="best")

    axes[-1].set_xlabel("Time" if use_time_axis else "Step")
    fig.suptitle("Performance Dashboard")
    fig.tight_layout(rect=[0, 0.03, 1, 0.97])
    dash_path = os.path.join(reports_dir, "performance_dashboard.png")
    fig.savefig(dash_path, dpi=150)
    plt.close(fig)

    # Summary markdown
    summary_path = os.path.join(reports_dir, "report.md")
    avg_turnover = float(np.mean(df_ts["turnover"].values)) if len(df_ts) > 0 else 0.0
    # Average holding period in steps
    holds = []
    last = None
    run_len = 0
    for a in actions_aligned:
        if last is None or a == last:
            run_len += 1
        else:
            holds.append(run_len)
            run_len = 1
        last = a
    if run_len > 0:
        holds.append(run_len)
    avg_hold = float(np.mean(holds)) if holds else 0.0

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"# Evaluation Report\n\n")
        f.write(f"- Steps: {int(len(out))}\n")
        f.write(f"- Switches: {int(num_switches)}\n")
        f.write(f"- Total Return: {total_return:.4f}\n")
        f.write(f"- Max Drawdown: {max_dd:.4f}\n")
        f.write(f"- Sharpe (ann.): {sharpe:.4f}\n")
        f.write(f"- Avg Turnover per step: {avg_turnover:.4f}\n")
        f.write(f"- Avg Holding Period (steps): {avg_hold:.1f}\n\n")
        f.write(f"Artifacts:\n")
        f.write(f"- Equity curve: equity_curve.png\n")
        f.write(f"- Dashboard: performance_dashboard.png\n")
        f.write(f"- Timeseries CSV: eval_timeseries.csv\n")

    return {
        "csv": csv_path,
        "plot": png_path,
        "dashboard": dash_path,
        "timeseries": ts_csv_path,
        "report": summary_path,
        "steps": int(len(out)),
        "switches": int(num_switches),
        "total_return": total_return,
        "max_drawdown": max_dd,
        "sharpe": sharpe,
        "model_path": model_path,
    }


def main():
    root = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(root, "data", "btc_usdc.csv")
    models_dir = os.path.join(root, "models")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Expected data at: {data_path}")
    if not os.path.isdir(models_dir):
        raise FileNotFoundError(f"Expected models directory at: {models_dir}")
    metrics = evaluate_model(models_dir=models_dir, data_path=data_path)
    print(metrics)


if __name__ == "__main__":
    main()


