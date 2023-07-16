# Prerequisite
```python3
Python >= 3.7
```

# Run
```python3
python -m src.ordermatch.main
```

# Test
```python3
python -m unittest
```

# Performance characteristics
## Determining whether an AddOrderRequest results in a match
Constant time.

## Removing filled orders from the resting order book
log<sub>2</sub>(number of orders with different prices)

## Removing a cancelled order (due to a CancelOrderRequest) from the orderbook.
Constant time.

# Design
Create a buy order heap and a sell order heap with every node in the heap being a FIFO list of same-price orders. The top element in the buy order heap has the highest price, which that in the sell order heap has the lowest price.

Maintain a hash map from order ID to the actual order. Upon cancellation, simply mark the order as cancelled, and the order would be lazily removed from the heap.

# Input sanity check
1. Contains non digit characters
2. Too few or too many fields
3. Order side field is neither 0 nor 1
4. Order to be cancelled does not exist or has already been cancelled
5. Message type is neither 0 nor 1