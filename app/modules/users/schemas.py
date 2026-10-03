from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from app.core.enum_data import PermissionEnum

class UserBase(BaseModel):
    username: str
    password: str
    email: EmailStr
    fullname: str
    age: int
    
class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    fullname: str
    age: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class PermissionResponse(BaseModel):
    permission: PermissionEnum
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)