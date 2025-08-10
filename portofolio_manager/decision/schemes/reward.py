from typing import List
import numpy as np
from tensortrade.env.default.rewards import RewardScheme


class RotationalRewardScheme(RewardScheme):
    """Downside-aware reward: Sortino-like with drawdown and switching costs.

    - Uses recent step returns buffer to compute mean and downside deviation
    - Penalizes max drawdown over the window
    - Penalizes allocation switching to discourage whipsaws
    """

    def __init__(
        self,
        window: int = 48,
        switch_penalty: float = 0.002,
        dd_penalty: float = 0.5,
        eps: float = 1e-8,
    ):
        super().__init__()
        self.window = window
        self.switch_penalty = switch_penalty
        self.dd_penalty = dd_penalty
        self.eps = eps

        self.prev_net_worth: float = 0.0
        self.prev_allocation: float | None = None
        self.returns: List[float] = []
        self.nw_history: List[float] = []

    def reset(self):
        self.prev_net_worth = 0.0
        self.prev_allocation = None
        self.returns = []
        self.nw_history = []

    def _max_drawdown(self, equity: np.ndarray) -> float:
        if equity.size < 2:
            return 0.0
        run_max = np.maximum.accumulate(equity)
        dd = (equity - run_max) / (run_max + self.eps)
        return float(dd.min())  # negative number

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

        self.nw_history.append(nw)
        if len(self.nw_history) > self.window:
            self.nw_history.pop(0)

        # Sortino-like: mean over downside deviation
        ret_arr = np.array(self.returns, dtype=float)
        mu = float(ret_arr.mean()) if ret_arr.size else 0.0
        downside = ret_arr[ret_arr < 0.0]
        dd_sigma = float(downside.std()) if downside.size else 0.0
        sortino_like = mu / (dd_sigma + self.eps)

        # Allocation switch cost based on value weights
        total_value = 0.0
        btc_value = 0.0
        for w in portfolio.wallets:
            if w.instrument.symbol.upper() == portfolio.base_instrument.symbol.upper():
                value = w.total_balance.as_float()
            else:
                pair = portfolio.base_instrument / w.instrument
                price = w.exchange.quote_price(pair)
                value = w.total_balance.as_float() * float(price)
            total_value += value
            if w.instrument.symbol.upper() == "BTC":
                btc_value += value
        alloc = btc_value / (total_value + self.eps) if total_value > 0 else 0.0
        if self.prev_allocation is None:
            switch_cost = 0.0
        else:
            switch_cost = abs(alloc - self.prev_allocation)
        self.prev_allocation = alloc

        # Drawdown penalty over recent window (negative number)
        eq = np.array(self.nw_history, dtype=float)
        max_dd = self._max_drawdown(eq)  # negative

        reward = sortino_like - self.switch_penalty * switch_cost + self.dd_penalty * max_dd
        return float(reward)


