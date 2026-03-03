from pydantic import BaseModel
from datetime import datetime

# 用户注册请求模型
class UserCreate(BaseModel):
    username: str
    password: str

# 用户登录请求模型
class UserLogin(BaseModel):
    username: str
    password: str

# 用户信息响应模型
class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 登录响应模型
class LoginResponse(BaseModel):
    access_token: str
    token_type: str

# 修改密码请求模型
class ChangePasswordRequest(BaseModel):
    new_password: str