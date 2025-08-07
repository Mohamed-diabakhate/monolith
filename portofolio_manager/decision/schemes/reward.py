from typing import List
import numpy as np
from tensortrade.env.default.rewards import RewardScheme


class RotationalRewardScheme(RewardScheme):
    """Sharpe-like reward with optional volatility and switching penalties."""

    def __init__(self, vol_penalty: float = 0.0, switch_penalty: float = 0.001, window: int = 30, eps: float = 1e-8):
        super().__init__()
        self.window = window
        self.vol_penalty = vol_penalty
        self.switch_penalty = switch_penalty
        self.eps = eps

        self.prev_net_worth: float = 0.0
        self.prev_allocation: float | None = None
        self.returns: List[float] = []

    def reset(self):
        self.prev_net_worth = 0.0
        self.prev_allocation = None
        self.returns = []

    def reward(self, env) -> float:
        portfolio = env.action_scheme.portfolio
        nw = float(portfolio.net_worth)
        if self.prev_net_worth == 0.0:
            self.prev_net_worth = nw
        step_ret = (nw - self.prev_net_worth) / (self.prev_net_worth + self.eps)
        self.prev_net_worth = nw

        self.returns.append(step_ret)
        if len(self.returns) > self.window:
            self.returns.pop(0)

        mu = float(np.mean(self.returns)) if self.returns else 0.0
        sigma = float(np.std(self.returns)) + self.eps
        sharpe_like = mu / sigma

        # Compute allocation to base (by value) from wallets
        # Compute allocation of BTC by value using exchange quote prices
        total_value = 0.0
        btc_value = 0.0
        for w in portfolio.wallets:
            if w.instrument.symbol.upper() == portfolio.base_instrument.symbol.upper():
                value = w.total_balance.as_float()
            else:
                pair = portfolio.base_instrument / w.instrument
                price = w.exchange.quote_price(pair)
                value = w.total_balance.as_float() / float(price) if pair.base.symbol == portfolio.base_instrument.symbol else w.total_balance.as_float() * float(price)
            total_value += value
            if w.instrument.symbol.upper() == "BTC":
                btc_value += value

        alloc = btc_value / (total_value + self.eps) if total_value > 0 else 0.0
        if self.prev_allocation is None:
            switch_cost = 0.0
        else:
            switch_cost = abs(alloc - self.prev_allocation)
        self.prev_allocation = alloc

        return float(sharpe_like - self.vol_penalty * sigma - self.switch_penalty * switch_cost)


