from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import OrderItem
from app.schemas.order_items import OrderItemCreate


class OrderItemService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_order_item_by_id(self, item_id: int) -> OrderItem | None:
        result = await self.db.execute(select(OrderItem).where(OrderItem.id == item_id))
        return result.scalars().first()

    async def list_order_items(self) -> list[OrderItem]:
        order_items = await self.db.execute(select(OrderItem))
        return order_items.scalars().all()

    async def create_order_item(self, item_data: OrderItemCreate) -> OrderItem:
        new_item = OrderItem(
            order_id = item_data.order_id,
            product_id = item_data.product_id,
            quantity = item_data.quantity,
            unit_price = item_data.unit_price,
        )
        self.db.add(new_item)
        await self.db.commit()
        await self.db.refresh(new_item)
        return new_item

    async def delete_order_item(self, item_id: int) -> None:
        order_item = await self.get_order_item_by_id(item_id)
        self.db.delete(order_item)
        await self.db.commit()

    async def update_order_item(
        self, item_id: int, item_data: OrderItemCreate
    ) -> OrderItem:
        order_item = await self.get_order_item_by_id(item_id)
        for key, value in item_data.model_dump().items():
            setattr(order_item, key, value)

        self.db.add(order_item)
        await self.db.commit()
        await self.db.refresh(order_item)
        return order_item
