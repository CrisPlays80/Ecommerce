from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Product
from app.schemas.products import ProductCreate


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_product(self, product_create: ProductCreate) -> Product:
        try:
            new_product = Product(
                sku=product_create.sku,
                name=product_create.name,
                description=product_create.description,
                price=product_create.price,
                stock_quantity=product_create.stock_quantity,
            )
            self.db.add(new_product)
            await self.db.commit()
            await self.db.refresh(new_product)
            return new_product
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=400, detail="Product with this SKU already exists"
            ) from None

    async def get_product_by_id(self, product_id: int) -> Product | None:
        product = await self.db.execute(select(Product).where(Product.product_id == product_id))
        product = product.scalars().first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    async def get_product_by_sku(self, sku: str) -> Product | None:
        product = await self.db.execute(select(Product).where(Product.sku == sku))
        product = product.scalars().first()
        if not product:
            raise HTTPException(status_code=400, detail="Product not found")
        return product

    async def list_products(self) -> list[Product]:
        result = await self.db.execute(select(Product))
        return result.scalars().all()
