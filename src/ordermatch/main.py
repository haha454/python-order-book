import sys

from src.ordermatch.book import OrderBook
from src.ordermatch.order import OrderSide, Order


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main():
    order_book = OrderBook()
    for line_no, line in enumerate(sys.stdin, start=1):
        if any(not field.strip().isdigit() for field in line.rstrip().split(',')):
            eprint(f'contains non digit characters, at line {line_no}: {line}')
            continue
        fields: list[int] = list(map(int, line.rstrip().split(',')))
        if fields[0] == 0:
            # AddOrderRequest
            if len(fields) != 5:
                eprint(f'AddOrderRequest should have 5 fields, at line {line_no}: {line}')
                continue
            if fields[2] not in set(member.value for member in OrderSide):
                eprint(f'unknown order side {fields[2]} at line {line_no}: {line}')
                continue
            order_id, order_side, quantity, price = fields[1], OrderSide(fields[2]), fields[3], fields[4]
            for trade in order_book.match_and_store(
                    Order(side=order_side, id=order_id, price=price, quantity=quantity)):
                print(str(trade))

        elif fields[0] == 1:
            # CancelOrderRequest
            if len(fields) != 2:
                eprint(f'CancelOrderRequest should have 2 fields, at line {line_no}: {line}')
                continue
            if not order_book.cancel(fields[1]):
                eprint(
                    f'unable to cancel order {fields[1]}, because the order does not exist or it has already been cancelled, at line {line_no}: {line}')
        else:
            eprint(f'unknown message type: {fields[0]}, at line {line_no}: {line}')


if __name__ == '__main__':
    main()
