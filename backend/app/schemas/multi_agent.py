from pydantic import BaseModel
from typing import Optional


class QueryRequest(BaseModel):
    query: str
    datasource_id: Optional[int] = None
    chat_id: Optional[str] = None


class QueryResponse(BaseModel):
    success: bool
    user_query: str
    generated_sql: Optional[str] = None
    final_sql: Optional[str] = None
    validation_result: Optional[dict] = None
    optimization_result: Optional[dict] = None
    error_message: Optional[str] = None
