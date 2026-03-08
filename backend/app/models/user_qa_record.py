from sqlalchemy import Column, BigInteger, String, Text, DateTime, Integer
from sqlalchemy.sql import func
from app.database.db import Base

class UserQARecord(Base):
    """问答记录表"""
    __tablename__ = "t_user_qa_record"
    __table_args__ = {"comment": "问答记录表"}

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(Integer, nullable=True, comment="用户ID")
    uuid = Column(String(200), nullable=True, comment="自定义ID")
    conversation_id = Column(String(100), nullable=True, comment="对话ID")
    message_id = Column(String(100), nullable=True, comment="消息ID")
    task_id = Column(String(100), nullable=True, comment="任务ID")
    chat_id = Column(String(100), nullable=True, comment="对话ID")
    question = Column(Text, nullable=True, comment="用户问题")
    to2_answer = Column(Text, nullable=True, comment="大模型答案")
    to4_answer = Column(Text, nullable=True, comment="业务数据")
    datasource_id = Column(BigInteger, nullable=True, comment="数据源ID")
    generated_sql = Column(Text, nullable=True, comment="原始生成的SQL（未优化，用于RAG检索）")
    sql_statement = Column(Text, nullable=True, comment="SQL语句（优化后的SQL（带注释，用于前端展示）")
    create_time = Column(DateTime, nullable=True, server_default=func.now(), comment="创建时间")
