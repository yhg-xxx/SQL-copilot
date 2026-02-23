import logging
from typing import Any, Dict
from langgraph.graph.state import CompiledStateGraph
from app.multi_agent.analysis.graph import create_multi_agent_graph
from app.multi_agent.state.agent_state import AgentState

logger = logging.getLogger(__name__)


class MultiAgent:
    """
    多智能体协作系统主类
    """

    def __init__(self):
        self.running_tasks = {}
        self.step_start_times = {}
        self.step_progress_ids = {}

    async def run_agent(
        self,
        query: str,
        response=None,
        chat_id: str = None,
        uuid_str: str = None,
        user_token=None,
        datasource_id: int = None,
    ) -> Dict[str, Any]:
        """
        运行多智能体系统
        
        Args:
            query: 用户输入的自然语言查询
            response: 响应对象（用于流式输出）
            chat_id: 会话ID
            uuid_str: 自定义任务ID
            user_token: 用户认证token
            datasource_id: 数据源ID
            
        Returns:
            包含最终结果的字典
        """
        logger.info(f"多智能体系统启动，查询: {query}")
        
        try:
            # 解析用户信息（简化版，后续可完善）
            user_id = 1
            if user_token:
                try:
                    from app.utils.jwt_utils import decode_jwt_token
                    user_dict = await decode_jwt_token(user_token)
                    user_id = user_dict.get("id", 1)
                except Exception as e:
                    logger.warning(f"解析用户token失败: {e}")
            
            # 初始化状态
            initial_state = AgentState(
                user_query=query,
                attempts=0,
                datasource_id=datasource_id,
                user_id=user_id,
            )
            
            # 创建图
            graph: CompiledStateGraph = create_multi_agent_graph()
            
            # 同步执行图（简单原型）
            final_state = None
            try:
                # 同步执行
                final_state = graph.invoke(initial_state)
            except Exception as e:
                logger.error(f"图执行失败: {e}", exc_info=True)
                initial_state["error_message"] = f"执行失败: {str(e)}"
                final_state = initial_state
            
            # 构建返回结果
            result = {
                "success": final_state.get("error_message") is None,
                "user_query": query,
                "generated_sql": final_state.get("generated_sql"),
                "final_sql": final_state.get("final_sql"),
                "validation_result": (
                    final_state.get("validation_result").model_dump()
                    if final_state.get("validation_result")
                    else None
                ),
                "optimization_result": (
                    final_state.get("optimization_result").model_dump()
                    if final_state.get("optimization_result")
                    else None
                ),
                "error_message": final_state.get("error_message"),
            }
            
            logger.info(f"多智能体系统执行完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"多智能体系统运行出错: {e}", exc_info=True)
            return {
                "success": False,
                "user_query": query,
                "error_message": str(e)
            }
