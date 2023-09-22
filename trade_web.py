from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from order_book import Order, OrderBook

app = FastAPI()
order_book = OrderBook()


class OrderRequest(BaseModel):
    name: str
    side: str
    price: float
    quantity: int
    owner: str


@app.get("/")
async def index():
    """
    返回撮合订单静态页面
    """
    with open("./index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/orders")
async def create_order(order_request: OrderRequest):
    order_id = len(order_book.order_id_to_order) + 1
    order = Order(
        name=order_request.name,
        order_id=order_id,
        side=order_request.side,
        price=order_request.price,
        quantity=order_request.quantity,
        owner=order_request.owner,
    )
    order_book.add_order(order)
    order_book.match_orders()
    return {"order_id": order_id}


@app.delete("/orders/{order_id}")
async def cancel_order(order_id: int):
    order_book.cancel_order(order_id)
    return {"message": "Order cancelled"}


@app.get("/order_book")
async def get_order_book():
    return {
        "sells": sum([v for v in order_book.sells.values()], []),
        "buys": sum([v for v in order_book.buys.values()], []),
    }


@app.get("/trades")
async def get_trades():
    return {"trades": order_book.trade_history}
