from typing import List
from gym.spaces import Discrete

from tensortrade.env.default.actions import TensorTradeActionScheme
from tensortrade.oms.orders import Order
from tensortrade.oms.orders.create import proportion_order
from tensortrade.oms.instruments import Instrument


class CapitalRotationScheme(TensorTradeActionScheme):
    """Discrete 2-action scheme to rotate fully between base and quote wallets.

    action 0 -> 100% base instrument (e.g., USDT)
    action 1 -> 100% quote instrument (e.g., BTC)
    """

    def __init__(self, base: Instrument, quote: Instrument):
        super().__init__()
        self._action_space = Discrete(2)
        self.base = base
        self.quote = quote

    @property
    def action_space(self) -> Discrete:
        return self._action_space

    def get_orders(self, action: int, portfolio) -> List[Order]:
        base_wallet = portfolio.get_wallet(portfolio.exchanges[0].id, self.base)
        quote_wallet = portfolio.get_wallet(portfolio.exchanges[0].id, self.quote)

        # Skip order if there is nothing to move from source
        min_abs = 1e-8
        if action == 0:
            # Move entirely into base (e.g., USDT) from quote (e.g., BTC)
            if quote_wallet.balance.as_float() <= min_abs:
                return []
            order = proportion_order(portfolio, source=quote_wallet, target=base_wallet, proportion=1.0)
            return [order]
        else:
            # Move entirely into quote (e.g., BTC) from base (e.g., USDT)
            if base_wallet.balance.as_float() <= min_abs:
                return []
            order = proportion_order(portfolio, source=base_wallet, target=quote_wallet, proportion=1.0)
            return [order]


class DiscreteAllocationScheme(TensorTradeActionScheme):
    """Discrete allocation scheme: target BTC allocation in value terms.

    The action maps to a target allocation for BTC between 0% and 100% in
    evenly spaced steps. The scheme computes the proportion of the source
    wallet required to rebalance toward the target in one step (bounded to 100%).

    Example with num_levels=5 -> targets: [0.0, 0.25, 0.5, 0.75, 1.0].
    """

    def __init__(self, base: Instrument, quote: Instrument, num_levels: int = 5, min_trade_value: float = 2.0):
        super().__init__()
        if num_levels < 2:
            raise ValueError("num_levels must be >= 2")
        self.base = base
        self.quote = quote
        self.num_levels = num_levels
        self.min_trade_value = float(min_trade_value)
        self._action_space = Discrete(num_levels)

    @property
    def action_space(self) -> Discrete:
        return self._action_space

    def _portfolio_values(self, portfolio) -> tuple[float, float, float]:
        """Return tuple (total_value_usdt, btc_value_usdt, base_value_usdt)."""
        base_wallet = portfolio.get_wallet(portfolio.exchanges[0].id, self.base)
        quote_wallet = portfolio.get_wallet(portfolio.exchanges[0].id, self.quote)

        # Price as USDT per BTC
        pair = portfolio.base_instrument / quote_wallet.instrument
        price = float(quote_wallet.exchange.quote_price(pair))

        base_value = base_wallet.total_balance.as_float()
        btc_units = quote_wallet.total_balance.as_float()
        btc_value = btc_units * price
        total_value = base_value + btc_value
        return total_value, btc_value, base_value

    def get_orders(self, action: int, portfolio) -> List[Order]:
        min_abs = 1e-8
        min_btc_qty = 1e-8  # respect BTC precision to avoid zero-quantity orders
        total_value, btc_value, base_value = self._portfolio_values(portfolio)

        if total_value <= min_abs:
            return []

        # Target allocation for BTC by value
        target_alloc = action / (self.num_levels - 1)
        target_btc_value = target_alloc * total_value

        # Current allocation
        current_btc_value = btc_value
        delta_value = target_btc_value - current_btc_value

        base_wallet = portfolio.get_wallet(portfolio.exchanges[0].id, self.base)
        quote_wallet = portfolio.get_wallet(portfolio.exchanges[0].id, self.quote)

        # Small value changes: skip to avoid micro trades and zero-commission rounding
        if abs(delta_value) < max(self.min_trade_value, 1e-3):
            return []

        # Move from base -> BTC
        if delta_value > 0 and base_value > min_abs:
            proportion = min(1.0, max(0.0, delta_value / (base_value + 1e-12)))
            # Estimated BTC to buy given this proportion
            pair = portfolio.base_instrument / self.quote
            price = float(base_wallet.exchange.quote_price(pair))
            est_btc = (base_value * proportion) / max(price, 1e-12)
            if proportion <= 1e-8 or est_btc < min_btc_qty:
                return []
            order = proportion_order(portfolio, source=base_wallet, target=quote_wallet, proportion=float(proportion))
            return [order]

        # Move from BTC -> base
        if delta_value < 0 and btc_value > min_abs:
            proportion = min(1.0, max(0.0, (-delta_value) / (btc_value + 1e-12)))
            # Estimated BTC to sell
            est_btc = (btc_value * proportion) / max(float(btc_value) if btc_value > 0 else 1.0, 1e-12)
            est_btc = quote_wallet.total_balance.as_float() * proportion
            if proportion <= 1e-8 or est_btc < min_btc_qty:
                return []
            order = proportion_order(portfolio, source=quote_wallet, target=base_wallet, proportion=float(proportion))
            return [order]

        return []

