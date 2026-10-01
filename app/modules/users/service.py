from app.modules.users import schemas, models
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import select
from app.core.security import get_password_hash
from app.core.enum_data import PermissionEnum

class UserService:
    
    @staticmethod
    async def register_user(user_data: schemas.UserCreate, db: AsyncSession) -> models.User:
        """
        Đăng ký người dùng mới.
        """
        # Kiểm tra xem username hoặc email đã tồn tại chưa
        existing_user = (await db.execute(
            select(models.User).where(models.User.username == user_data.username)
        )).scalars().first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username đã tồn tại."
            )
        
        existing_user = (await db.execute(
            select(models.User).where(models.User.email == user_data.email)
        )).scalars().first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã tồn tại."
            )
        # Khởi tạo user mới với 3 permission mặc định: VIEW_USER, VIEW_PROJECT, VIEW_TASK
        stmt = (
            select(models.Permission)
            .where(models.Permission.permission.in_([PermissionEnum.VIEW_USER, PermissionEnum.VIEW_PROJECT, PermissionEnum.VIEW_TASK]))
        )
        default_perms = (await db.execute(stmt)).scalars().all()
        
        new_user = models.User(
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            email=user_data.email,
            fullname=user_data.fullname,
            age=user_data.age
        )
        new_user.has_permissions.extend(default_perms)
        db.add(new_user)
        await db.flush()
        await db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    async def get_all_users(db: AsyncSession) -> list[models.User]:
        """
        Lấy danh sách tất cả người dùng.
        """
        users = (await db.execute(select(models.User))).scalars().all()
        return users

        