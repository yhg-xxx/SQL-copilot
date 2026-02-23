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


class OptimizationResult(BaseModel):
    """
    SQL 优化结果
    """
    optimized: bool
    optimized_sql: Optional[str] = None
    suggestions: Optional[List[str]] = None
    execution_notes: Optional[str] = None


class AgentState(TypedDict):
    """
    多智能体系统状态定义
    """
    user_query: str
    db_info: Optional[Dict]
    generated_sql: Optional[str]
    validation_result: Optional[ValidationResult]
    optimized_sql: Optional[str]
    optimization_result: Optional[OptimizationResult]
    final_sql: Optional[str]
    execution_result: Optional[Any]
    attempts: int
    datasource_id: Optional[int]
    user_id: Optional[int]
    error_message: Optional[str]
