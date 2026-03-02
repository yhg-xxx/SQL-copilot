from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# 对话创建请求模型
class ConversationCreate(BaseModel):
    title: str
    conversation_type: Optional[str] = "general"

# 对话更新请求模型
class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    status: Optional[str] = None

# 对话响应模型
class ConversationResponse(BaseModel):
    id: int
    user_id: int
    conversation_id: str
    title: str
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    conversation_type: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 对话列表响应模型
class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int
