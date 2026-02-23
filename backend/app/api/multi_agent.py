from fastapi import APIRouter, HTTPException, status
from app.multi_agent.multi_agent import MultiAgent
from app.schemas.multi_agent import QueryRequest, QueryResponse


router = APIRouter(prefix="/multi-agent", tags=["multi-agent"])

multi_agent_instance = MultiAgent()


@router.post("/query", response_model=QueryResponse)
async def multi_agent_query(
    request: QueryRequest,
):
    """
    多智能体查询接口
    
    Args:
        request: 查询请求
        
    Returns:
        查询结果
    """
    try:
        user_token = None
        # 尝试从请求头获取 token
        for key, value in request.__dict__.items():
            if key == 'credentials':
                user_token = value
        
        result = await multi_agent_instance.run_agent(
            query=request.query,
            datasource_id=request.datasource_id,
            chat_id=request.chat_id,
            user_token=user_token
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-agent query failed: {str(e)}"
        )



