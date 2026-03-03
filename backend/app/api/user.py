from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, LoginResponse, ChangePasswordRequest
from app.utils.jwt_utils import get_password_hash, verify_password, create_access_token
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/user", tags=["user"])

# 用户注册接口
@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        password_hash=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully", "user_id": new_user.id}

# 用户登录接口
@router.post("/login", response_model=LoginResponse)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    # 查找用户
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成令牌
    access_token = create_access_token(
        data={"sub": str(db_user.id), "username": db_user.username}
    )
    
    return {"access_token": access_token, "token_type": "Bearer"}

# 获取当前用户信息
@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return current_user


# 修改密码接口
@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改当前登录用户的密码
    
    Args:
        request: 包含新密码的请求
        current_user: 当前登录用户信息
        db: 数据库会话
        
    Returns:
        修改成功的消息
    """
    user_id = int(current_user.get("sub"))
    
    # 查找用户
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 验证新密码长度
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    # 更新密码
    hashed_password = get_password_hash(request.new_password)
    db_user.password_hash = hashed_password
    
    db.commit()
    db.refresh(db_user)
    
    return {"message": "Password changed successfully"}