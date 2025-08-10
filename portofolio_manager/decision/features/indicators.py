import pandas as pd
import pandas_ta as ta


def build_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add common momentum and volatility indicators.

    Expects columns: open, high, low, close, volume
    Returns a new DataFrame with indicators and no NA rows.
    """
    out = df.copy()

    # Momentum
    out["rsi"] = ta.rsi(out["close"], length=14)
    out["roc"] = ta.roc(out["close"], length=10)
    out["ema_fast"] = ta.ema(out["close"], length=12)
    out["ema_slow"] = ta.ema(out["close"], length=26)
    macd = ta.macd(out["close"], fast=12, slow=26, signal=9)
    if macd is not None:
        for col in macd.columns:
            out[col] = macd[col]

    # Volatility
    out["atr"] = ta.atr(high=out["high"], low=out["low"], close=out["close"], length=14)
    bb = ta.bbands(out["close"], length=20, std=2.0)
    if bb is not None:
        for col in bb.columns:
            out[col] = bb[col]
        out["bb_width"] = (out[bb.columns[-1]] - out[bb.columns[0]]) / (out["close"] + 1e-8)

    # Drop NA from indicator warmups
    out = out.dropna()
    return out


