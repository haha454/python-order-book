from unittest import TestCase

from src.ordermatch.book import OrderBook
from src.ordermatch.order import Order, OrderSide
from src.ordermatch.trade import Trade, PartialOrderFill, FullOrderFill


class TestOrderBook(TestCase):
    def test_match_no_trade_when_order_book_is_empty(self):
        order_book = OrderBook()
        self.assertFalse(order_book.match_and_store(Order(id=12345, side=OrderSide.BUY, quantity=2, price=50)))

    def test_match_sell_order_with_the_buy_order_with_highest_price(self):
        order_book = OrderBook()
        order_book.match_and_store(Order(id=10000, side=OrderSide.BUY, quantity=4, price=50))
        order_book.match_and_store(Order(id=10001, side=OrderSide.BUY, quantity=3, price=40))
        order_book.match_and_store(Order(id=10002, side=OrderSide.BUY, quantity=10, price=30))
        self.assertEqual([Trade(quantity=4, price=50,
                                aggressive_order_fill=PartialOrderFill(order_id=20003, new_quantity=1),
                                resting_order_fill=FullOrderFill(order_id=10000)),
                          Trade(quantity=1, price=40,
                                aggressive_order_fill=FullOrderFill(order_id=20003),
                                resting_order_fill=PartialOrderFill(order_id=10001, new_quantity=2))],
                         order_book.match_and_store(Order(id=20003, side=OrderSide.SELL, quantity=5, price=15)))

    def test_match_buy_order_with_the_seller_order_with_lowest_price(self):
        order_book = OrderBook()
        order_book.match_and_store(Order(id=10000, side=OrderSide.SELL, quantity=4, price=30))
        order_book.match_and_store(Order(id=10001, side=OrderSide.SELL, quantity=3, price=40))
        order_book.match_and_store(Order(id=10002, side=OrderSide.SELL, quantity=10, price=50))
        self.assertEqual([Trade(quantity=4, price=30,
                                aggressive_order_fill=PartialOrderFill(order_id=20003, new_quantity=3),
                                resting_order_fill=FullOrderFill(order_id=10000)),
                          Trade(quantity=3, price=40,
                                aggressive_order_fill=FullOrderFill(order_id=20003),
                                resting_order_fill=FullOrderFill(order_id=10001))],
                         order_book.match_and_store(Order(id=20003, side=OrderSide.BUY, quantity=7, price=100)))

    def test_match_oldest_order_when_price_is_the_same(self):
        order_book = OrderBook()
        order_book.match_and_store(Order(id=10000, side=OrderSide.SELL, quantity=4, price=50))
        order_book.match_and_store(Order(id=10001, side=OrderSide.SELL, quantity=3, price=50))
        self.assertEqual([Trade(quantity=4, price=50,
                                aggressive_order_fill=PartialOrderFill(order_id=20003, new_quantity=1),
                                resting_order_fill=FullOrderFill(order_id=10000)),
                          Trade(quantity=1, price=50,
                                aggressive_order_fill=FullOrderFill(order_id=20003),
                                resting_order_fill=PartialOrderFill(order_id=10001, new_quantity=2))],
                         order_book.match_and_store(Order(id=20003, side=OrderSide.BUY, quantity=5, price=100)))

    def test_cancel_nonexistent_order_should_return_false(self):
        order_book = OrderBook()
        order_book.match_and_store(Order(id=10000, side=OrderSide.SELL, quantity=4, price=50))
        self.assertFalse(order_book.cancel(999))

    def test_cancel_cancelled_order_should_return_false(self):
        order_book = OrderBook()
        order_book.match_and_store(Order(id=10000, side=OrderSide.SELL, quantity=4, price=50))
        order_book.cancel(10000)
        self.assertFalse(order_book.cancel(10000))

    def test_cancel_normal_order_should_return_true(self):
        order_book = OrderBook()
        order_book.match_and_store(Order(id=10000, side=OrderSide.SELL, quantity=4, price=50))
        self.assertTrue(order_book.cancel(10000))

    def test_match_no_cancelled_order(self):
        order_book = OrderBook()
        order_book.match_and_store(Order(id=10000, side=OrderSide.BUY, quantity=4, price=50))
        order_book.match_and_store(Order(id=10001, side=OrderSide.BUY, quantity=3, price=40))
        order_book.cancel(10000)
        self.assertEqual([Trade(quantity=3, price=40,
                                aggressive_order_fill=FullOrderFill(order_id=20003),
                                resting_order_fill=FullOrderFill(order_id=10001))],
                         order_book.match_and_store(Order(id=20003, side=OrderSide.SELL, quantity=3, price=15)))
