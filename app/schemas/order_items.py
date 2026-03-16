from pydantic import BaseModel, ConfigDict

from app.schemas.orders import OrderRead
from app.schemas.products import ProductRead


class OrderItemCreate(BaseModel):
    quantity: int
    unit_price: float
    discount: float | None = 0.0
    order_id: int
    product_id: int


class OrderItemRead(BaseModel):
    order_item_id: int
    quantity: int
    unit_price: float
    discount: float | None = 0.0
    order_id: int
    product_id: int

    model_config = ConfigDict(from_attributes=True)


class OrderItemReadWithRelations(OrderItemRead):
    order: OrderRead
    product: ProductRead
