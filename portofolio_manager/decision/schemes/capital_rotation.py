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


