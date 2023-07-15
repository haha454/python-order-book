from enum import Enum
from dataclasses import dataclass


class OrderSide(Enum):
    BUY = 0
    SELL = 1


@dataclass
class Order:
    id: int
    side: OrderSide
    quantity: int
    price: int
    cancelled: bool = False

    def reduce_quantity(self, delta: int):
        self.quantity -= delta
