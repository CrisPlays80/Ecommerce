import asyncio

import jwt
from fastapi import HTTPException
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.db.models import User
from app.schemas.enums import UserRole
from app.schemas.users import UserCreate, UserPasswordUpdate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_current_user(self, token: str) -> User:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )

        except (ExpiredSignatureError, InvalidTokenError):
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            ) from None

        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )

        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    async def list_users(self) -> list[User]:
        query = await self.db.execute(select(User))
        return query.scalars().all()

    async def get_user_by_id(self, user_id: int) -> User:
        result = await self.db.execute(select(User).filter(User.user_id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).filter(User.email == email))
        result = result.scalars().first()
        return result

    async def create_user(self, user_create: UserCreate) -> User:
        try:
            hashed_password = await asyncio.to_thread(
                get_password_hash, user_create.password
            )

            new_user = User(
                email=user_create.email,
                full_name=user_create.full_name,
                hashed_password=hashed_password,
            )

            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            return new_user

        except IntegrityError:
            await self.db.rollback()
            raise (
                HTTPException(status_code=400, detail="Email already registered")
                ) from None
        
        except ValueError as e:
            raise (
                HTTPException(status_code=400, detail=str(e))
                ) from None

    async def authenticate_user(self, email: str, password: str) -> User | None:
        user = await self.get_user_by_email(email)

        if not user:
            return None

        is_valid = await asyncio.to_thread(
            verify_password, password, user.hashed_password
        )

        if not is_valid:
            return None
        return user

    async def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        user = await self.get_user_by_id(user_id)

        if user_update.full_name is not None:
            user.full_name = user_update.full_name
        if user_update.email is not None:
            existing_user = await self.get_user_by_email(user_update.email)
            if existing_user and existing_user.user_id != user_id:
                raise HTTPException(status_code=400, detail="Email already registered")
            user.email = user_update.email

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_password(
        self, user_id: int, password_update: UserPasswordUpdate
    ) -> None:
        user = await self.get_user_by_id(user_id)

        is_valid = await asyncio.to_thread(
            verify_password, password_update.current_password, user.hashed_password
        )

        if not is_valid:
            raise HTTPException(status_code=400, detail="Incorrect password")

        hashed_password = await asyncio.to_thread(
            get_password_hash, password_update.new_password
        )
        user.hashed_password = hashed_password

        await self.db.commit()
        await self.db.refresh(user)

    async def delete_user(self, user_id: int):
        user = await self.get_user_by_id(user_id)
        if user.role == UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Admin users cannot be deleted")
        await self.db.delete(user)
        await self.db.commit()
