from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.multi_agent.multi_agent import MultiAgent
from app.schemas.multi_agent import QueryRequest, QueryResponse
from app.utils.dependencies import get_current_user
from app.database.db import get_db
from app.models.user_qa_record import UserQARecord
from app.models.conversation import UserConversation
from app.utils.title_generator import generate_conversation_title
from app.multi_agent.agents.conversation_summarizer import stream_conversation_summary
# RAG功能已移除
import uuid
import json
from typing import AsyncGenerator

router = APIRouter(prefix="/multi-agent", tags=["multi-agent"])

multi_agent_instance = MultiAgent()

@router.post("/query/stream")
async def multi_agent_query_stream(
        request: QueryRequest,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """
    流式多智能体查询接口
    先返回SQL结果，然后流式输出对话总结
    """
    try:
        user_id = int(current_user.get("sub"))

        # ========== 第一步：立即创建问答记录（只包含问题） ==========
        current_message_id = str(uuid.uuid4())
        qa_record = None
        
        if request.chat_id:
            try:
                # 先创建问答记录，只包含基本信息
                qa_record = UserQARecord(
                    user_id=user_id,
                    conversation_id=request.chat_id,
                    message_id=current_message_id,
                    chat_id=request.chat_id,
                    question=request.query,
                    datasource_id=request.datasource_id,
                    to2_answer="",  # 初始为空，后续更新
                    to4_answer="",  # 初始为空，后续更新
                    generated_sql="",  # 初始为空，后续更新
                    sql_statement=""  # 初始为空，后续更新
                )
                db.add(qa_record)
                db.commit()
                db.refresh(qa_record)
                logging.info(f"创建问答记录成功，ID: {qa_record.id}")
            except Exception as e:
                import logging
                logging.error(f"创建问答记录失败: {e}")
        # ===========================================================

        # 运行多智能体系统生成SQL
        result = await multi_agent_instance.run_agent(
            query=request.query,
            datasource_id=request.datasource_id,
            chat_id=request.chat_id,
            user_id=user_id
        )

        # 获取对话历史用于总结
        chat_history = []
        if request.chat_id:
            try:
                history = db.query(UserQARecord).filter(
                    UserQARecord.conversation_id == request.chat_id,
                    UserQARecord.user_id == user_id
                ).order_by(UserQARecord.create_time.asc()).all()
                
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
            except Exception as e:
                pass

        # 用于收集流式输出的总结内容
        summary_content_list = []
        query_data_for_save = None

        async def stream_generator() -> AsyncGenerator[str, None]:
            nonlocal summary_content_list, query_data_for_save
            
            # 先发送SQL结果
            yield f"data: {json.dumps({'type': 'sql_result', 'data': result}, ensure_ascii=False, default=str)}\n\n"
            
            # 然后流式输出对话总结
            if chat_history or result.get("sql_execution_result"):
                async for chunk in stream_conversation_summary(
                    chat_history=chat_history,
                    user_query=request.query,
                    sql_execution_result=result.get("sql_execution_result")
                ):
                    # chunk 格式: {"type": "content", "content": "..."} 或 {"type": "data", ...}
                    if chunk.get("type") == "content":
                        content = chunk.get('content', '')
                        summary_content_list.append(content)
                        yield f"data: {json.dumps({'type': 'summary', 'content': content}, ensure_ascii=False)}\n\n"
                    elif chunk.get("type") == "data":
                        query_data_for_save = chunk.get('query_result_data')
                        yield f"data: {json.dumps({'type': 'summary_data', 'query_result_data': query_data_for_save}, ensure_ascii=False, default=str)}\n\n"
                    elif chunk.get("type") == "error":
                        yield f"data: {json.dumps({'type': 'error', 'content': chunk.get('content', '')}, ensure_ascii=False)}\n\n"
            
            # ========== 第二步：更新问答记录（添加总结、SQL等信息） ==========
            if request.chat_id and qa_record:
                try:
                    # 完整的总结内容
                    full_summary = ''.join(summary_content_list)
                    
                    # to4_answer 存储数据表格和图表信息（JSON格式）
                    sql_exec_result = result.get("sql_execution_result") or {}
                    to4_data = {
                        "query_data": sql_exec_result.get("data") or [],
                        "columns": sql_exec_result.get("columns") or [],
                        "row_count": sql_exec_result.get("row_count") or 0
                    }
                    
                    import logging
                    logging.info(f"更新问答记录，ID: {qa_record.id}")
                    
                    # 更新问答记录
                    qa_record.to2_answer = full_summary  # 总结内容
                    qa_record.to4_answer = json.dumps(to4_data, ensure_ascii=False, default=str)  # 数据表格信息
                    qa_record.generated_sql = result.get("validated_sql", "")  # 原始未优化SQL，用于RAG检索
                    qa_record.sql_statement = result.get("final_sql", "")  # 优化后的SQL，用于前端展示
                    db.commit()
                    db.refresh(qa_record)

                    # RAG功能已移除

                    conversation = db.query(UserConversation).filter(
                        UserConversation.conversation_id == request.chat_id,
                        UserConversation.user_id == user_id
                    ).first()
                    
                    if conversation and conversation.title == "新对话":
                        new_title = generate_conversation_title(request.query)
                        conversation.title = new_title
                        db.commit()
                        db.refresh(conversation)
                        
                        # 发送标题更新事件给前端
                        yield f"data: {json.dumps({'type': 'title_update', 'title': new_title}, ensure_ascii=False)}\n\n"
                except Exception as e:
                    import logging
                    logging.error(f"更新问答记录失败: {e}")
            # ==========================================================
            
            # 发送完成信号
            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
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

# 非流式多智能体查询接口，以弃用！
@router.post("/query", response_model=QueryResponse)
async def multi_agent_query(
        request: QueryRequest,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """
    多智能体查询接口

    Args:
        request: 查询请求

    Returns:
        查询结果
        :param db:
        :param request:
        :param current_user:
    """
    try:
        user_id = int(current_user.get("sub"))

        result = await multi_agent_instance.run_agent(
            query=request.query,
            datasource_id=request.datasource_id,
            chat_id=request.chat_id,
            user_id=user_id
        )

        # 保存对话历史
        if request.chat_id:
            # 生成唯一的消息ID
            message_id = str(uuid.uuid4())

            # 创建问答记录
            qa_record = UserQARecord(
                user_id=user_id,
                conversation_id=request.chat_id,
                message_id=message_id,
                chat_id=request.chat_id,
                question=request.query,
                to2_answer=result.get("final_sql", ""),
                datasource_id=request.datasource_id,
                generated_sql=result.get("validated_sql", ""),  # 原始未优化SQL，用于RAG检索
                sql_statement=result.get("final_sql", "")  # 优化后的SQL，用于前端展示
            )

            db.add(qa_record)
            db.commit()
            db.refresh(qa_record)

            # RAG功能已移除
            
            # 检查是否是对话的第一条消息，如果是，生成标题
            from app.models.conversation import UserConversation
            from app.utils.title_generator import generate_conversation_title
            
            # 查询对话
            conversation = db.query(UserConversation).filter(
                UserConversation.conversation_id == request.chat_id,
                UserConversation.user_id == user_id
            ).first()
            
            # 检查对话是否存在，且标题为默认的"新对话"
            if conversation and conversation.title == "新对话":
                # 生成新标题
                new_title = generate_conversation_title(request.query)
                # 更新对话标题
                conversation.title = new_title
                db.commit()
                db.refresh(conversation)

        return QueryResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-agent query failed: {str(e)}"
        )