from dataclasses import dataclass
from typing import ClassVar, Union


@dataclass(frozen=True)
class FullOrderFill:
    MSG_TYPE: ClassVar[int] = 3

    order_id: int

    def __str__(self):
        return f'{self.MSG_TYPE},{self.order_id}'


@dataclass(frozen=True)
class PartialOrderFill:
    MSG_TYPE: ClassVar[int] = 4

    order_id: int
    new_quantity: int

    def __str__(self):
        return f'{self.MSG_TYPE},{self.order_id},{self.new_quantity}'


@dataclass
class Trade:
    MSG_TYPE: ClassVar[int] = 2

    quantity: int
    price: int
    aggressive_order_fill: Union[PartialOrderFill, FullOrderFill]
    resting_order_fill: Union[PartialOrderFill, FullOrderFill]

    def __str__(self):
        return f'{self.MSG_TYPE},{self.quantity},{self.price}\n{str(self.aggressive_order_fill)}\n{str(self.resting_order_fill)}'
