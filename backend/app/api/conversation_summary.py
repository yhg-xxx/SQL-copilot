from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, AsyncGenerator
from app.utils.dependencies import get_current_user
from app.database.db import get_db
from app.models.user_qa_record import UserQARecord
from app.multi_agent.state.agent_state import AgentState
from app.multi_agent.agents.conversation_summarizer import conversation_summarizer, stream_conversation_summary
from app.multi_agent.agents.datasource_utils import get_datasource_config
from app.multi_agent.agents.sql_executor import execute_sql_with_database
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversation", tags=["conversation-summary"])


class SummaryRequest(BaseModel):
    """总结请求"""
    chat_id: str
    datasource_id: Optional[int] = None


class SummaryResponse(BaseModel):
    """总结响应"""
    success: bool
    summary: Optional[str] = None
    key_topics: Optional[List[str]] = None
    sql_queries: Optional[List[Dict[str, Any]]] = None
    statistics: Optional[Dict[str, Any]] = None
    insights: Optional[List[str]] = None
    query_result_data: Optional[Dict[str, Any]] = None  # 查询结果数据
    error: Optional[str] = None


@router.post("/summary", response_model=SummaryResponse)
async def get_conversation_summary(
    request: SummaryRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取对话总结，包含表格和图表数据
    
    Args:
        request: 总结请求
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        总结结果（包含查询结果数据）
    """
    try:
        user_id = int(current_user.get("sub"))
        
        # 获取对话历史
        chat_history = []
        last_sql_result = None
        
        try:
            history = db.query(UserQARecord).filter(
                UserQARecord.conversation_id == request.chat_id,
                UserQARecord.user_id == user_id
            ).order_by(UserQARecord.create_time.asc()).all()
            
            # 格式化历史记录
            for record in history:
                if record.question:
                    chat_history.append({
                        "role": "user",
                        "content": record.question,
                        "timestamp": record.create_time
                    })
                if record.to2_answer:
                    chat_history.append({
                        "role": "assistant",
                        "content": record.to2_answer,
                        "timestamp": record.create_time,
                        "sql": record.sql_statement
                    })
            
            logger.info(f"获取到 {len(chat_history)} 条对话历史记录")
            
            # 获取最后一次查询的结果（如果存在SQL语句，重新执行获取结果）
            if history and request.datasource_id:
                # 找到最后一条有SQL的记录
                last_sql_record = None
                for record in reversed(history):
                    if record.sql_statement:
                        last_sql_record = record
                        break
                
                if last_sql_record and last_sql_record.sql_statement:
                    logger.info(f"找到最后一条SQL: {last_sql_record.sql_statement[:100]}...")
                    try:
                        # 获取数据源配置
                        datasource_config = get_datasource_config(request.datasource_id)
                        if datasource_config:
                            # 创建临时状态用于执行SQL
                            temp_state = {"final_sql": last_sql_record.sql_statement}
                            exec_result = execute_sql_with_database(temp_state, datasource_config)
                            
                            if exec_result.get("success"):
                                last_sql_result = {
                                    "columns": exec_result.get("columns", []),
                                    "data": exec_result.get("data", []),
                                    "row_count": exec_result.get("row_count", 0)
                                }
                                logger.info(f"重新执行SQL成功，获取到 {last_sql_result['row_count']} 条记录")
                            else:
                                logger.warning(f"重新执行SQL失败: {exec_result.get('error')}")
                    except Exception as sql_err:
                        logger.error(f"重新执行SQL时出错: {sql_err}")
                
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取对话历史失败: {str(e)}"
            )
        
        if not chat_history:
            return SummaryResponse(
                success=False,
                error="没有找到对话历史记录"
            )
        
        # 初始化状态
        initial_state = AgentState(
            user_query="生成对话总结",
            attempts=0,
            datasource_id=request.datasource_id,
            user_id=user_id,
            chat_history=chat_history,
            sql_execution_result=last_sql_result
        )
        
        # 调用总结智能体
        final_state = conversation_summarizer(initial_state)
        
        # 获取总结结果
        summary_result = final_state.get("summary_result")
        
        if not summary_result:
            return SummaryResponse(
                success=False,
                error="生成总结失败"
            )
        
        return SummaryResponse(
            success=summary_result.success,
            summary=summary_result.summary,
            key_topics=summary_result.key_topics,
            sql_queries=summary_result.sql_queries,
            statistics=summary_result.statistics,
            insights=summary_result.insights,
            query_result_data=summary_result.query_result_data,
            error=summary_result.error
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成对话总结失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成对话总结失败: {str(e)}"
        )


@router.get("/summary/stream")
async def stream_conversation_summary_api(
    chat_id: str = Query(..., description="对话ID"),
    datasource_id: Optional[int] = Query(None, description="数据源ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    流式获取对话总结
    
    Args:
        chat_id: 对话ID
        datasource_id: 数据源ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        SSE流式响应
    """
    try:
        user_id = int(current_user.get("sub"))
        
        # 获取对话历史
        chat_history = []
        last_sql_result = None
        
        try:
            history = db.query(UserQARecord).filter(
                UserQARecord.conversation_id == chat_id,
                UserQARecord.user_id == user_id
            ).order_by(UserQARecord.create_time.asc()).all()
            
            # 格式化历史记录
            for record in history:
                if record.question:
                    chat_history.append({
                        "role": "user",
                        "content": record.question,
                        "timestamp": record.create_time
                    })
                if record.to2_answer:
                    chat_history.append({
                        "role": "assistant",
                        "content": record.to2_answer,
                        "timestamp": record.create_time,
                        "sql": record.sql_statement
                    })
            
            logger.info(f"[流式总结] 获取到 {len(chat_history)} 条对话历史记录")
            
            # 获取最后一次查询的结果
            if history and datasource_id:
                last_sql_record = None
                for record in reversed(history):
                    if record.sql_statement:
                        last_sql_record = record
                        break
                
                if last_sql_record and last_sql_record.sql_statement:
                    logger.info(f"[流式总结] 找到最后一条SQL: {last_sql_record.sql_statement[:100]}...")
                    try:
                        datasource_config = get_datasource_config(datasource_id)
                        if datasource_config:
                            temp_state = {"final_sql": last_sql_record.sql_statement}
                            exec_result = execute_sql_with_database(temp_state, datasource_config)
                            
                            if exec_result.get("success"):
                                last_sql_result = {
                                    "columns": exec_result.get("columns", []),
                                    "data": exec_result.get("data", []),
                                    "row_count": exec_result.get("row_count", 0)
                                }
                                logger.info(f"[流式总结] 重新执行SQL成功，获取到 {last_sql_result['row_count']} 条记录")
                    except Exception as sql_err:
                        logger.error(f"[流式总结] 重新执行SQL时出错: {sql_err}")
                        
        except Exception as e:
            logger.error(f"[流式总结] 获取对话历史失败: {e}")
            async def error_generator():
                yield f"data: {json.dumps({'type': 'error', 'content': f'获取对话历史失败: {str(e)}'}, ensure_ascii=False)}\n\n"
            return StreamingResponse(
                error_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*"
                }
            )
        
        if not chat_history:
            async def empty_generator():
                yield f"data: {json.dumps({'type': 'error', 'content': '没有找到对话历史记录'}, ensure_ascii=False)}\n\n"
            return StreamingResponse(
                empty_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*"
                }
            )
        
        # 创建流式生成器
        async def summary_stream_generator() -> AsyncGenerator[str, None]:
            try:
                async for chunk in stream_conversation_summary(
                    chat_history=chat_history,
                    user_query="生成对话总结",
                    sql_execution_result=last_sql_result
                ):
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                
                # 发送完成信号
                yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                logger.error(f"[流式总结] 生成过程出错: {e}")
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            summary_stream_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"[流式总结] 失败: {e}", exc_info=True)
        async def error_generator():
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"
        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*"
            }
        )
