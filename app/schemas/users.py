from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.enums import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str | None
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.CUSTOMER


class UserUpdate(BaseModel):
    full_name: str | None
    email: EmailStr | None


class UserPasswordUpdate(BaseModel):
    current_password: str = Field(..., min_length=8, description="Current password of the user")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password for the user")


class UserRead(BaseModel):
    user_id: int
    email: EmailStr
    full_name: str | None
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
