# from typing import List, Dict
# from shared.models.portfolio_position import PortfolioPosition

# def calc_portfolio_current_value(positions: List[PortfolioPosition], current_prices: Dict[int, float]) -> int:
#     total_value=0
#     for position in positions:
#         total_value+=position.quantity * current_prices[position.asset_id]
#     return total_value

# def calc_position_current_value(position: PortfolioPosition, current_prices: Dict[int, float]) -> float:
#     return position.quantity * current_prices[position.asset_id]

class Trade:
    def __init__(self, asset_id, price, quantity, direction):
        self.asset_id = asset_id
        self.price = price
        self.quantity = quantity
        self.direction = direction

portfolio_trades = [
    Trade(asset_id=1, price=30, quantity=50, direction="buy"),
    Trade(asset_id=1, price=50, quantity=30, direction="buy"),
    Trade(asset_id=1, price=80, quantity=30, direction="sell"),
    Trade(asset_id=2, price=10, quantity=30, direction="buy"),
    Trade(asset_id=2, price=5, quantity=10, direction="sell"),
]
from collections import deque

def calc_unrealized_pnl(portfolio_trades): #portfolio_trades sort asc
    id_to_lot = dict() # {asset_id: deque(qty: price, qty: price)} - онли покупки а вычитаем только если встречаем продажу
    
    for t in portfolio_trades:
        if t.asset_id not in id_to_lot:
            id_to_lot[t.asset_id] = deque()
        if t.direction == "buy":
            id_to_lot[t.asset_id].append({"qty" : t.quantity, "price": t.price})
        elif t.direction == "sell":
            left_to_sell = t.quantity
            
            while left_to_sell != 0:
                left_in_lot = id_to_lot[t.asset_id][0]["qty"]
                if left_in_lot > left_to_sell:
                    left_in_lot -= left_to_sell
                    left_to_sell = 0
                    id_to_lot[t.asset_id][0]["qty"] = left_in_lot
                elif left_in_lot < left_to_sell:
                    left_to_sell -= left_in_lot
                    id_to_lot[t.asset_id].popleft()
                else: 
                    left_to_sell -= left_in_lot
                    id_to_lot[t.asset_id].popleft()
    id_to_lot = {k : v for k, v in id_to_lot.items() if v}
    current_price = 150
    mid_prices = {}
    quantities = {}
    for a_id, lots in id_to_lot.items():
        mid_prices[a_id] = sum([(lot["qty"] * lot["price"]) for lot in lots]) / sum([lot["qty"] for lot in lots])
        quantities[a_id] = sum(lot["qty"] for lot in lots)
    
    absolute_profit = sum(current_price * quantities[a_id] - mid_prices[a_id] * quantities[a_id] for a_id in id_to_lot.keys())
    print(id_to_lot)
    return absolute_profit
print(calc_unrealized_pnl(portfolio_trades=portfolio_trades))