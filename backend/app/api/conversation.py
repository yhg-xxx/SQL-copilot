from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.conversation import UserConversation
from app.models.user_qa_record import UserQARecord
from app.schemas.conversation import ConversationCreate, ConversationUpdate, ConversationResponse, ConversationListResponse
from app.utils.dependencies import get_current_user
import uuid

router = APIRouter(prefix="/conversations", tags=["conversation"])

# 创建对话
@router.post("", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # 生成唯一的对话ID
    conversation_id = str(uuid.uuid4())
    
    # 创建新对话
    new_conversation = UserConversation(
        user_id=int(current_user["sub"]),
        conversation_id=conversation_id,
        title=conversation.title,
        conversation_type=conversation.conversation_type
    )
    
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    
    return new_conversation

# 获取用户的对话列表
@router.get("", response_model=ConversationListResponse)
async def get_conversations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # 查询用户的对话列表
    conversations = db.query(UserConversation).filter(
        UserConversation.user_id == int(current_user["sub"])
    ).order_by(UserConversation.updated_at.desc()).offset(skip).limit(limit).all()
    
    # 计算总数
    total = db.query(UserConversation).filter(
        UserConversation.user_id == int(current_user["sub"])
    ).count()
    
    return ConversationListResponse(
        conversations=conversations,
        total=total
    )

# 获取单个对话详情
@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # 查询对话
    conversation = db.query(UserConversation).filter(
        UserConversation.conversation_id == conversation_id,
        UserConversation.user_id == int(current_user["sub"])
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return conversation

# 获取对话历史记录
@router.get("/{conversation_id}/history")
async def get_conversation_history(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # 查询对话是否存在
    conversation = db.query(UserConversation).filter(
        UserConversation.conversation_id == conversation_id,
        UserConversation.user_id == int(current_user["sub"])
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # 查询对话历史记录
    history = db.query(UserQARecord).filter(
        UserQARecord.conversation_id == conversation_id
    ).order_by(UserQARecord.create_time.asc()).all()
    
    # 查询该对话最后使用的数据源ID
    last_datasource_id = None
    if history:
        # 从最新的记录开始查找有数据源ID的记录
        for record in reversed(history):
            if record.datasource_id:
                last_datasource_id = record.datasource_id
                break
    
    # 格式化历史记录
    formatted_history = []
    for record in history:
        if record.question:
            formatted_history.append({
                "role": "user",
                "content": record.question,
                "timestamp": record.create_time
            })
        if record.to2_answer:
            formatted_history.append({
                "role": "assistant",
                "content": record.to2_answer,
                "timestamp": record.create_time,
                "sql": record.sql_statement
            })
    
    return {
        "history": formatted_history,
        "last_datasource_id": last_datasource_id
    }

# 更新对话
@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    conversation_update: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # 查询对话
    conversation = db.query(UserConversation).filter(
        UserConversation.conversation_id == conversation_id,
        UserConversation.user_id == int(current_user["sub"])
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # 更新对话信息
    update_data = conversation_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(conversation, field, value)
    
    db.commit()
    db.refresh(conversation)
    
    return conversation

# 删除对话
@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # 查询对话
    conversation = db.query(UserConversation).filter(
        UserConversation.conversation_id == conversation_id,
        UserConversation.user_id == int(current_user["sub"])
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # 删除对话相关的历史记录
    db.query(UserQARecord).filter(
        UserQARecord.conversation_id == conversation_id
    ).delete()
    
    # 删除对话
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversation deleted successfully"}
