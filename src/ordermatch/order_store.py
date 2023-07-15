import heapq
from collections import deque
from dataclasses import dataclass, InitVar, field
from typing import Optional

from src.ordermatch.order import Order, OrderSide


@dataclass
class SamePriceOrders:
    price: int
    side: OrderSide
    order: InitVar[Optional[Order]]

    def __post_init__(self, order: Optional[Order]):
        self._orders: deque[Order] = deque([order]) if order else deque()

    def __lt__(self, other) -> bool:
        return self.price < other.price if self.side == OrderSide.SELL else self.price > other.price

    def get_earliest_order(self) -> Optional[Order]:
        self._purge_cancelled_or_empty_orders()
        return self._orders[0] if self._orders else None

    def add_order(self, order: Order) -> None:
        self._orders.append(order)

    def _purge_cancelled_or_empty_orders(self) -> None:
        while self._orders and (self._orders[0].cancelled or self._orders[0].quantity == 0):
            self._orders.popleft()


@dataclass
class OrderStore:
    _order_heap: list[SamePriceOrders] = field(default_factory=list)
    _orders_per_price: dict[int, SamePriceOrders] = field(default_factory=dict)

    def _maintain_orders(self) -> None:
        while self._order_heap and not self._order_heap[0].get_earliest_order():
            del self._orders_per_price[heapq.heappop(self._order_heap).price]

    def has_order(self) -> bool:
        self._maintain_orders()
        return self._order_heap and self._order_heap[0].get_earliest_order() is not None

    def get_best_order(self) -> Optional[Order]:
        self._maintain_orders()
        return self._order_heap[0].get_earliest_order() if self._order_heap else None

    def add_order(self, order: Order) -> None:
        if order.price in self._orders_per_price:
            self._orders_per_price[order.price].add_order(order)
        else:
            self._orders_per_price[order.price] = SamePriceOrders(
                order.price, order.side, order)
            heapq.heappush(self._order_heap,
                           self._orders_per_price[order.price])
