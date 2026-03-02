from fastapi import APIRouter, HTTPException, status, Depends
from app.multi_agent.multi_agent import MultiAgent
from app.schemas.multi_agent import QueryRequest, QueryResponse
from app.utils.dependencies import get_current_user


router = APIRouter(prefix="/multi-agent", tags=["multi-agent"])

multi_agent_instance = MultiAgent()


@router.post("/query", response_model=QueryResponse)
async def multi_agent_query(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    多智能体查询接口
    
    Args:
        request: 查询请求
        
    Returns:
        查询结果
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
        
        return QueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-agent query failed: {str(e)}"
        )



