from collections import deque
import sqlite3


class Order:
    def __init__(self, name, order_id, side, price, quantity, owner):
        self.name = name
        self.order_id = order_id
        self.side = side
        self.price = price
        self.quantity = quantity
        self.owner = owner


class Trade:
    def __init__(self, trade_id, buy_order_id, sell_order_id, price, quantity, owner):
        self.trade_id = trade_id
        self.buy_order_id = buy_order_id
        self.sell_order_id = sell_order_id
        self.price = price
        self.quantity = quantity
        self.owner = owner


class OrderBook:
    def __init__(self):
        conn = sqlite3.connect("orders.db")
        c = conn.cursor()
        # 从 orders 表中加载订单
        c.execute("SELECT * FROM orders")
        orders = c.fetchall()
        self.order_id_to_order = {}
        self.buys = {}
        self.sells = {}
        for order in orders:
            name, order_id, side, price, quantity, owner = order
            order = Order(
                name=name,
                order_id=order_id,
                side=side,
                price=price,
                quantity=quantity,
                owner=owner,
            )
            self.order_id_to_order[order_id] = order
            if side == "buy":
                self.buys.setdefault(order.name, [])
                self.buys[order.name].append(order)
                self.buys[order.name].sort(key=lambda x: x.price, reverse=True)
            else:
                self.sells.setdefault(order.name, [])
                self.sells[order.name].append(order)
                self.sells[order.name].sort(key=lambda x: x.price)

        # 从 trades 表中加载交易
        c.execute("SELECT * FROM trades")
        trades = c.fetchall()
        self.trade_history = []
        for trade in trades:
            buy_order_id, sell_order_id, price, quantity, owner = trade
            buy_order = self.order_id_to_order[buy_order_id]
            sell_order = self.order_id_to_order[sell_order_id]
            trade = Trade(
                buy_order=buy_order,
                sell_order=sell_order,
                price=price,
                quantity=quantity,
            )
            self.trade_history.append(trade)

        # 关闭连接
        conn.close()

    def add_order(self, order):
        # 增加的订单需要记录到sqlite
        # 连接到 SQLite 数据库
        conn = sqlite3.connect("orders.db")
        c = conn.cursor()
        # 将订单插入到 orders 表中
        c.execute(
            "INSERT INTO orders (name, order_id, side, price, quantity, owner) VALUES (?, ?, ?, ?, ?, ?)",
            (
                order.name,
                order.order_id,
                order.side,
                order.price,
                order.quantity,
                order.owner,
            ),
        )
        # 提交更改并关闭连接
        conn.commit()
        conn.close()
        self.order_id_to_order[order.order_id] = order
        if order.side == "buy":
            self.buys.setdefault(order.name, [])
            self.buys[order.name].append(order)
            self.buys[order.name].sort(key=lambda x: x.price, reverse=True)
        else:
            self.sells.setdefault(order.name, [])
            self.sells[order.name].append(order)
            self.sells[order.name].sort(key=lambda x: x.price)

    def cancel_order(self, order_id):
        order = self.order_id_to_order[order_id]
        del self.order_id_to_order[order_id]
        if order.side == "buy":
            self.buys[order.name].remove(order)
        else:
            self.sells[order.name].remove(order)

    def match_orders_for_product(self, product):
        while len(self.buys[product]) > 0 and len(self.sells[product]) > 0:
            best_buy = self.buys[product][0]
            best_sell = self.sells[product][0]
            if best_buy.price >= best_sell.price:
                quantity = min(best_buy.quantity, best_sell.quantity)
                trade = Trade(
                    trade_id=len(self.trade_history) + 1,
                    buy_order_id=best_buy.order_id,
                    sell_order_id=best_sell.order_id,
                    price=best_buy.price,
                    quantity=quantity,
                )
                self.trade_history.append(trade)
                best_buy.quantity -= quantity
                best_sell.quantity -= quantity
                if best_buy.quantity == 0:
                    self.buys[product].pop(0)
                if best_sell.quantity == 0:
                    self.sells[product].pop(0)
                # 将撮合成功的订单插入到 trades 表中
                conn = sqlite3.connect("orders.db")
                c = conn.cursor()
                c.execute(
                    "INSERT INTO trades (buy_order_id, sell_order_id, price, quantity) VALUES (?, ?, ?, ?)",
                    (best_buy.order_id, best_sell.order_id, best_buy.price, quantity),
                )
                conn.commit()
                conn.close()
            else:
                break

    def match_orders(self):
        # 撮合成功的数据写入到sqlite
        for k in set(self.buys.keys()) & set(self.sells.keys()):
            self.match_orders_for_product(k)


if __name__ == "__main__":
    import sqlite3

    # 连接到 SQLite 数据库
    conn = sqlite3.connect("orders.db")
    c = conn.cursor()
    # 删除 orders 表
    c.execute("DROP TABLE IF EXISTS orders")
    # 删除 trades 表
    c.execute("DROP TABLE IF EXISTS trades")

    # 创建 orders 表
    c.execute(
        """CREATE TABLE orders
                (name text, order_id integer, side text, price real, quantity integer, owner text)"""
    )

    # 创建 trades 表
    c.execute(
        """CREATE TABLE trades
                (trade_id integer, buy_order_id integer, sell_order_id integer, price real, quantity integer, owner text)"""
    )

    # 提交更改并关闭连接
    conn.commit()
    conn.close()

    order_book = OrderBook()

    # Add some orders to the order book
    order_book.add_order(
        Order(order_id=1, name="产品A", owner="jason", side="buy", price=100, quantity=10)
    )
    order_book.add_order(
        Order(order_id=2, name="产品A", owner="kale", side="sell", price=110, quantity=5)
    )
    order_book.add_order(
        Order(order_id=3, name="产品B", owner="jack", side="sell", price=105, quantity=7)
    )

    # Match some orders
    order_book.match_orders()

    # Cancel an order
    order_book.cancel_order(1)

    # Generate a report
    report = order_book.trade_history
    print(report)
