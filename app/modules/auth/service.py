from fastapi import Response, HTTPException, status
from app.modules.auth import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app.modules.users import models as user_models
from app.modules.auth import models as auth_models
from app.core.security import (
    SECRET_KEY,
    ALGORITHM,
    verify_password, 
    create_access_token,
    create_refresh_token,
    REFRESH_TOKEN_EXPIRE_DAYS
)
import jwt
from jwt.exceptions import (
    InvalidTokenError,
    ExpiredSignatureError
)
from datetime import datetime, timezone
from app.core.config import settings

class AuthService:
    
    @staticmethod
    async def login_user(response: Response, username: str, password: str, db: AsyncSession) -> schemas.LoginResponse:
        """
        Xác thực người dùng và trả về access token.
        """
        query = (
            select(user_models.User)
            .where(user_models.User.username == username)
            .options(selectinload(user_models.User.has_permissions))  # Load permissions cùng lúc
        )
        user = (await db.execute(query)).scalars().first()

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "Sai username hoặc password",
                    "type": "invalid_credentials"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Chuẩn OAuth2 quy định claim 'sub' là string
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token, refresh_token_expire = create_refresh_token(data={"sub": str(user.id)})

        # Lưu refresh token vào database
        new_refresh_token = auth_models.RefreshToken(
            token_string=refresh_token,
            user_id=user.id,
            expires_at=refresh_token_expire
        )
        
        db.add(new_refresh_token)
        await db.flush()
        
        # Gắn vào cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,                                                      # Chống XSS (JS không đọc được)
            secure=False if settings.ENVIRONMENT != "production" else True,     # Đổi thành True khi chạy HTTPS Production
            samesite="lax" if settings.ENVIRONMENT != "production" else "none",                                                     # Chống CSRF
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            path="/auth"                                                        # Chỉ gửi cookie cho các endpoint bắt đầu bằng /auth
        )
        
        return schemas.LoginResponse(
            access_token=access_token, 
            token_type="bearer",
            permissions=[perm.permission for perm in user.has_permissions]
        )
        
    @staticmethod
    async def refresh_access_token(response: Response, refresh_token: str, db: AsyncSession) -> schemas.Token:
        """
        Làm mới access token bằng refresh token.
        """
        # Giải mã refresh token
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "message": "Token không phải là refresh token",
                        "type": "invalid_refresh_token"
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )
            user_id_str: str | None = payload.get("sub")
            
            if not user_id_str:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "message": "Không tìm thấy id người dùng từ refresh token",
                        "type": "invalid_refresh_token"
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            user_id = int(user_id_str)
        except ExpiredSignatureError:
            response.delete_cookie(
                key="refresh_token",
                httponly=True,                                                      # Chống XSS (JS không đọc được)
                secure=False if settings.ENVIRONMENT != "production" else True,     # Đổi thành True khi chạy HTTPS Production
                samesite="lax" if settings.ENVIRONMENT != "production" else "none",  
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "Refresh token đã hết hạn",
                    "type": "expired_refresh_token"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )       
        except (InvalidTokenError, ValueError):
            response.delete_cookie(
                key="refresh_token",
                httponly=True,                                                      # Chống XSS (JS không đọc được)
                secure=False if settings.ENVIRONMENT != "production" else True,     # Đổi thành True khi chạy HTTPS Production
                samesite="lax" if settings.ENVIRONMENT != "production" else "none",                  
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "Refresh token không hợp lệ",
                    "type": "invalid_refresh_token"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Kiểm tra refresh token trong database
        query = (
            select(auth_models.RefreshToken)
            .where(auth_models.RefreshToken.token_string == refresh_token)
        )
        saved_token = (await db.execute(query)).scalars().first()
        
        if saved_token and saved_token.revoked:
        # Hủy toàn bộ token của user này để bảo vệ tài khoản
            revoke_all_stmt = (
                update(auth_models.RefreshToken)
                .where(auth_models.RefreshToken.user_id == user_id)
                .values(revoked=True)
            )
            await db.execute(revoke_all_stmt)
            await db.flush()
        
            response.delete_cookie(
                key="refresh_token",
                httponly=True,                                                      # Chống XSS (JS không đọc được)
                secure=False if settings.ENVIRONMENT != "production" else True,     # Đổi thành True khi chạy HTTPS Production
                samesite="lax" if settings.ENVIRONMENT != "production" else "none",                  
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "Refresh token bị tái sử dụng bất thường",
                    "type": "invalid_refresh_token"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Nếu không tìm thấy hoặc đã hết hạn
        if not saved_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "Refresh token không hợp lệ",
                    "type": "invalid_refresh_token"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        if saved_token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "Refresh token đã hết hạn",
                    "type": "expired_refresh_token"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
            
            
        # Rotate refresh token: hủy token cũ và tạo token mới
        saved_token.revoked = True
        # Tạo access token mới
        new_access_token = create_access_token(data={"sub": str(user_id)})
        new_refresh_token, new_refresh_token_expire = create_refresh_token(data={"sub": str(user_id)})
        
        # Lưu refresh token mới vào database
        new_refresh_token_entry = auth_models.RefreshToken(
            token_string=new_refresh_token,
            user_id=user_id,
            expires_at=new_refresh_token_expire
        )
        db.add(new_refresh_token_entry)
        await db.flush()
        
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,    
            httponly=True,                                                      # Chống XSS (JS không đọc được)
            secure=False if settings.ENVIRONMENT != "production" else True,     # Đổi thành True khi chạy HTTPS Production
            samesite="lax" if settings.ENVIRONMENT != "production" else "none",                                                     # Chống CSRF
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            path="/auth"                                                        # Chỉ gửi cookie cho các endpoint bắt đầu bằng /auth
        )
        
        return schemas.Token(access_token=new_access_token, token_type="bearer")
    
    @staticmethod
    async def logout_user(response: Response, refresh_token: str, db: AsyncSession):
        if refresh_token:
        # Đánh dấu revoked = True trong Database để không bao giờ dùng lại được nữa
            stmt = (
                update(auth_models.RefreshToken)
                .where(auth_models.RefreshToken.token_string == refresh_token)
                .values(revoked=True)
            )
            await db.execute(stmt)
            await db.flush()

        # Xóa Cookie khỏi trình duyệt client
        response.delete_cookie(
            key="refresh_token",
            httponly=True,
            secure=False if settings.ENVIRONMENT != "production" else True,
            samesite="lax" if settings.ENVIRONMENT != "production" else "none",
        )
        return None