# SimpleMatch

这是一个建议的撮合系统，用于撮合买家和卖家之间的交易。该系统使用Python编写，使用FastAPI框架提供RESTful API。
简易撮合系统
这是一个简易的撮合系统，用于匹配买单和卖单，以实现交易。

系统架构
该系统由以下几个部分组成：

trade_web.py：Web 服务器，用于接收订单请求和取消订单请求。
order_book.py：订单簿，用于存储所有订单，并匹配买单和卖单。

安装
克隆该仓库
安装Python 3.7或更高版本
安装依赖项：pip install -r requirements.txt
运行
进入项目目录
运行应用程序：uvicorn trade_web:app --reload

打开浏览器，访问 http://localhost:8000/，即可进入撮合订单静态页面。

创建订单：在页面上填写订单信息，点击“提交”按钮即可创建订单。

取消订单：在页面上找到要取消的订单，点击“取消”按钮即可取消订单。

API 文档
GET /
返回撮合订单静态页面。

POST /orders
创建订单。

请求参数：
name：订单名称。
side：订单方向，取值为 buy 或 sell。
price：订单价格。
quantity：订单数量。
owner：订单所有者。

响应参数：

order_id：订单 ID。

