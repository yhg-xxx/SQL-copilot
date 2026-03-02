from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database.db import Base

class UserConversation(Base):
    """用户对话表"""
    __tablename__ = "t_user_conversation"
    __table_args__ = {"comment": "用户对话表"}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    conversation_id = Column(String(100), unique=True, nullable=False, index=True, comment="对话唯一标识")
    title = Column(String(255), nullable=False, comment="对话标题")
    last_message = Column(Text, nullable=True, comment="最后一条消息")
    last_message_time = Column(DateTime, nullable=True, comment="最后一条消息时间")
    conversation_type = Column(String(50), nullable=False, default="general", comment="对话类型")
    status = Column(String(20), nullable=False, default="active", comment="对话状态")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
