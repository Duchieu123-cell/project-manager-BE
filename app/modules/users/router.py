from fastapi import APIRouter, status
from app.modules.users import schemas
from app.core.dependencies import (
    DBSession,
    VIEW_USER_PERMISSION
)
from app.modules.users.service import UserService


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post(
    "/register", 
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký người dùng mới"
)
async def register_user(
    user: schemas.UserCreate,
    db: DBSession
):
    return await UserService.register_user(user, db)

@router.get(
    "",
    response_model=list[schemas.UserResponse],
    summary="Lấy danh sách tất cả người dùng"
)
async def get_all_users(
    db: DBSession,
    current_user: VIEW_USER_PERMISSION
):
    return await UserService.get_all_users(db)