from fastapi import APIRouter, Depends

from app.api.v1.deps import CurrentUser, RoleChecker, get_user_service
from app.schemas.auth import Message
from app.schemas.enums import UserRole
from app.schemas.users import UserCreate, UserPasswordUpdate, UserRead, UserUpdate
from app.services.user_logic import UserService

router = APIRouter()

admin_role_checker = RoleChecker(allowed_roles=[UserRole.ADMIN])


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: CurrentUser):
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_current_user(
    user_update: UserUpdate,
    current_user: CurrentUser,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_user(current_user.user_id, user_update)


@router.patch("/me/password", response_model=Message)
async def update_current_user_password(
    password_update: UserPasswordUpdate,
    current_user: CurrentUser,
    user_service: UserService = Depends(get_user_service),
):
    await user_service.update_password(current_user.user_id, password_update)
    return Message(message="Password updated successfully")

@router.delete("/me", response_model=Message)
async def delete_current_user(
    current_user: CurrentUser, user_service: UserService = Depends(get_user_service)
):
    await user_service.delete_user(current_user.user_id)
    return Message(message=f"User {current_user.user_id} deleted successfully")


@router.get(
    "/{user_id}", response_model=UserRead, dependencies=[Depends(admin_role_checker)]
)
async def read_user(
    user_id: int, user_service: UserService = Depends(get_user_service)
):
    return await user_service.get_user_by_id(user_id)


@router.get("/", response_model=list[UserRead])
async def read_users(user_service: UserService = Depends(get_user_service)):
    users = await user_service.list_users()
    return users


@router.post("/", response_model=UserRead)
async def create_user(
    user: UserCreate, user_service: UserService = Depends(get_user_service)
):
    user_db = await user_service.create_user(user)
    return user_db


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_user(user_id, user_update)


@router.put("/{user_id}/password", response_model=UserRead, dependencies= [Depends(admin_role_checker)])
async def update_password(
    user_id: int,
    password_update: UserPasswordUpdate,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_password(user_id, password_update)


@router.delete(
    "/{user_id}", dependencies=[Depends(admin_role_checker)], response_model=Message
)
async def delete_user(
    user_id: int, user_service: UserService = Depends(get_user_service)
):
    await user_service.delete_user(user_id)
    return Message(message=f"User {user_id} deleted successfully")
