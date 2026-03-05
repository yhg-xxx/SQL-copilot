from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from backend.app.multi_agent.multi_agent import MultiAgent
from app.schemas.multi_agent import QueryRequest, QueryResponse
from app.utils.dependencies import get_current_user
from app.database.db import get_db
from app.models.user_qa_record import UserQARecord
import uuid

router = APIRouter(prefix="/multi-agent", tags=["multi-agent"])

multi_agent_instance = MultiAgent()


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
                sql_statement=result.get("final_sql", "")
            )

            db.add(qa_record)
            db.commit()
            
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