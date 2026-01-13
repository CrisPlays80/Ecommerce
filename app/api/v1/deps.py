from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_db
from app.schemas.enums import UserRole
from app.services.order_items_logic import OrderItemService
from app.services.orders_logic import OrderService
from app.services.product_logic import ProductService
from app.services.user_logic import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> User:
    return await user_service.get_current_user(token)


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(db)


async def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(db)


async def get_order_item_service(
    db: AsyncSession = Depends(get_db),
) -> OrderItemService:
    return OrderItemService(db)


class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Insufficient permissions"
            )
        return current_user
