from pydantic import BaseModel
from app.core.enum_data import PermissionEnum
    
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginResponse(Token):
    permissions: list[PermissionEnum] = []