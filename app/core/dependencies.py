from app.core.database import get_db, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.modules.users import models
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.core.config import settings
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.core.enum_data import PermissionEnum
from app.core.security import get_password_hash

DBSession = Annotated[AsyncSession, Depends(get_db)]
Token = Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="/auth/token"))]

async def get_current_user(access_token: Token, db: DBSession) -> models.User:
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str | None = payload.get("sub")
        
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Không thể định danh người dùng từ token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        user_id = int(user_id_str)
            

    except (InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    stmt = (
        select(models.User)
        .where(models.User.id == user_id)
        .options(selectinload(models.User.has_permissions))
    )
        
    user = (await db.execute(stmt)).scalars().first()
            
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không thể định danh người dùng từ token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user
        
CurrentUser = Annotated[models.User, Depends(get_current_user)]


class PermissionChecker:
    def __init__(self, required_permission: PermissionEnum):
        self.required_permission = required_permission

    async def __call__(self, current_user: CurrentUser) -> models.User:
        has_permission = (self.required_permission in [perm.permission for perm in current_user.has_permissions])
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập."
            )
            
        return current_user



UPDATE_PROJECT_PERMISSION = Annotated[models.User, Depends(PermissionChecker(PermissionEnum.UPDATE_PROJECT))]
DELETE_PROJECT_PERMISSION = Annotated[models.User, Depends(PermissionChecker(PermissionEnum.DELETE_PROJECT))]
VIEW_PROJECT_PERMISSION = Annotated[models.User, Depends(PermissionChecker(PermissionEnum.VIEW_PROJECT))]
CREATE_PROJECT_PERMISSION = Annotated[models.User, Depends(PermissionChecker(PermissionEnum.CREATE_PROJECT))]
UPDATE_TASK_PERMISSION = Annotated[models.User, Depends(PermissionChecker(PermissionEnum.UPDATE_TASK))]
DELETE_TASK_PERMISSION = Annotated[models.User, Depends(PermissionChecker(PermissionEnum.DELETE_TASK))]
VIEW_TASK_PERMISSION = Annotated[models.User, Depends(PermissionChecker(PermissionEnum.VIEW_TASK))]
CREATE_TASK_PERMISSION = Annotated[models.User, Depends(PermissionChecker(PermissionEnum.CREATE_TASK))]
VIEW_USER_PERMISSION = Annotated[models.User, Depends(PermissionChecker(PermissionEnum.VIEW_USER))]


async def load_permissions():
    """ 
    Khởi tạo permissions trong cơ sở dữ liệu nếu chưa tồn tại.
    """
    async with AsyncSessionLocal() as db:
        try:
            for perm in PermissionEnum:
                existing_permission = (await db.execute(
                    select(models.Permission).where(models.Permission.permission == perm)
                )).scalars().first()
            
                if not existing_permission:
                    new_permission = models.Permission(permission=perm)
                    db.add(new_permission)
                    await db.flush()
            
            await db.commit()      
        except Exception as e:
            await db.rollback()
            raise e
        finally:
            await db.close()
            
            
async def create_admin():
    """
    Tạo người dùng admin nếu chưa tồn tại.
    """
    async with AsyncSessionLocal() as db:
        try:
            existing_admin = (await db.execute(
                select(models.User).where(models.User.email == "admin@example.com")
            )).scalars().first()
    
            if not existing_admin:
                admin_user = models.User(
                    username="admin123",
                    hashed_password=get_password_hash("Admin123@"),
                    email="admin@example.com",
                    fullname="Admin User",
                    age=30
                )
                all_permissions = (await db.execute(select(models.Permission))).scalars().all()
                admin_user.has_permissions.extend(all_permissions)
                db.add(admin_user)
                await db.flush()
                await db.commit()
                
        except Exception as e:
            await db.rollback()
            raise e
        finally:
            await db.close()
