from typing import Optional, Dict, List, Any
from pydantic import BaseModel
from typing_extensions import TypedDict


class ValidationResult(BaseModel):
    """
    SQL 验证结果
    """
    valid: bool
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    mysql_validation_passed: Optional[bool] = None
    llm_validation_passed: Optional[bool] = None
    mysql_explain_result: Optional[str] = None
    llm_feedback: Optional[str] = None


class OptimizationResult(BaseModel):
    """
    SQL 优化结果
    """
    optimized: bool
    optimized_sql: Optional[str] = None
    suggestions: Optional[List[str]] = None
    execution_notes: Optional[str] = None


class ExecutionResult(BaseModel):
    """
    SQL 执行结果
    """
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[str]] = None
    row_count: Optional[int] = None
    error: Optional[str] = None


class SummaryResult(BaseModel):
    """
    对话总结结果
    """
    success: bool
    summary: Optional[str] = None
    key_topics: Optional[List[str]] = None
    sql_queries: Optional[List[Dict[str, Any]]] = None
    statistics: Optional[Dict[str, Any]] = None
    insights: Optional[List[str]] = None
    query_result_data: Optional[Dict[str, Any]] = None  # 查询结果数据
    error: Optional[str] = None


class AgentState(TypedDict):
    """
    多智能体系统状态定义
    """
    user_query: str  # 用户输入的自然语言查询
    db_info: Optional[str]  # 数据库表结构信息（已格式化）
    generated_sql: Optional[str]  # 初始生成的 SQL 语句
    validated_sql: Optional[str]  # 语法验证成功后的 SQL 语句（未优化，用于RAG检索）
    validation_result: Optional[ValidationResult]  # SQL 语法验证结果
    optimized_sql: Optional[str]  # 优化后的 SQL 语句
    optimization_result: Optional[OptimizationResult]  # SQL 优化结果
    final_sql: Optional[str]  # 最终可执行的 SQL 语句
    execution_result: Optional[ExecutionResult]  # SQL 执行结果
    sql_execution_result: Optional[Dict[str, Any]]  # SQL 语句执行后返回的数据结果（包含列和数据）
    datasource_id: Optional[int]  # 数据源 ID
    user_id: Optional[int]  # 用户 ID
    error_message: Optional[str]  # 错误信息
    chat_history: Optional[List[Dict[str, Any]]]  # 对话历史记录
    summary_result: Optional[SummaryResult]  # 对话总结结果
    db_type: Optional[str] # 数据源类型
    fix_attempts:int # 修复次数
    was_fixed: bool # 是否修复成功
    fix_explanation: Optional[str] # 修复描述
    retrieved_examples: Optional[List[Dict[str, Any]]] # RAG检索到的历史示例
    db_errors:Optional[List[Dict[str, Any]]]  # 数据库验证返回的错误
    datasource_config: Optional[Dict[str, Any]]  # 数据源连接配置（缓存，避免重复查询数据库）
