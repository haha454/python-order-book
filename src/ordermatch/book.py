from dataclasses import dataclass, field
from typing import Callable, Union

from src.ordermatch.order import Order, OrderSide
from src.ordermatch.order_store import OrderStore
from src.ordermatch.trade import Trade, PartialOrderFill, FullOrderFill


@dataclass
class OrderBook:
    _buy_order_store: OrderStore = field(default_factory=OrderStore)
    _sell_order_store: OrderStore = field(default_factory=OrderStore)
    _order_per_id: dict[int, Order] = field(default_factory=dict)

    def match_and_store(self, order: Order) -> list[Trade]:
        if order.quantity <= 0:
            return []
        if order.side == OrderSide.SELL:
            return self._match_and_store(
                order, self._buy_order_store, self._sell_order_store,
                lambda resting_order_price: order.price <= resting_order_price)
        elif order.side == OrderSide.BUY:
            return self._match_and_store(
                order, self._sell_order_store, self._buy_order_store,
                lambda resting_order_price: order.price >= resting_order_price)
        else:
            raise ValueError(f'unknown order side {order.side}')

    def _match_and_store(self, aggressive_order: Order, resting_order_store: OrderStore,
                         aggressive_order_store: OrderStore,
                         matching_predict: Callable[[int], bool]) -> list[Trade]:
        trades = []
        while resting_order_store.has_order() and aggressive_order.quantity and matching_predict(
                resting_order_store.get_best_order().price):
            resting_order = resting_order_store.get_best_order()
            trade = self._create_trade(aggressive_order=aggressive_order, resting_order=resting_order)
            trades.append(trade)
            aggressive_order.reduce_quantity(trade.quantity)
            resting_order.reduce_quantity(trade.quantity)

        if aggressive_order.quantity:
            aggressive_order_store.add_order(aggressive_order)

            assert aggressive_order.id not in self._order_per_id
            self._order_per_id[aggressive_order.id] = aggressive_order

        return trades

    @classmethod
    def _create_trade(cls, aggressive_order: Order, resting_order: Order) -> Trade:
        quantity = min(aggressive_order.quantity, resting_order.quantity)
        return Trade(quantity=quantity,
                     price=resting_order.price,
                     aggressive_order_fill=cls._create_order_fill(aggressive_order.id,
                                                                  aggressive_order.quantity - quantity),
                     resting_order_fill=cls._create_order_fill(resting_order.id,
                                                               resting_order.quantity - quantity))

    @classmethod
    def _create_order_fill(cls, order_id: int, new_quantity: int) -> Union[FullOrderFill, PartialOrderFill]:
        return PartialOrderFill(order_id=order_id, new_quantity=new_quantity) if new_quantity else FullOrderFill(
            order_id=order_id)

    def cancel(self, order_id: int) -> bool:
        """
        Cancels an order.
        :return: False if order_id does not exist or the order has already been cancelled.
        """
        if order_id not in self._order_per_id or self._order_per_id[order_id].cancelled:
            return False

        self._order_per_id[order_id].cancelled = True
        return True
