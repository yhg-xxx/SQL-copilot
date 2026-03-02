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
        user_id: int = 1,
        datasource_id: int = None,
    ) -> Dict[str, Any]:
        """
        运行多智能体系统

        Args:
            query: 用户输入的自然语言查询
            response: 响应对象（用于流式输出）
            chat_id: 会话ID
            uuid_str: 自定义任务ID
            user_id: 用户ID
            datasource_id: 数据源ID

        Returns:
            包含最终结果的字典
        """
        logger.info(f"多智能体系统启动，查询: {query}")

        try:
            logger.info(f"当前用户ID: {user_id}")

        # 获取对话历史
        chat_history = []
        if chat_id:
            try:
                from app.database.db import SessionLocal
                from app.models.user_qa_record import UserQARecord
                db = SessionLocal()
                try:
                    # 查询对话历史记录
                    history = db.query(UserQARecord).filter(
                        UserQARecord.conversation_id == chat_id
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
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"获取对话历史失败: {e}")

        # 初始化状态
        initial_state = AgentState(
            user_query=query,
            attempts=0,
            datasource_id=datasource_id,
            user_id=user_id,
            chat_history=chat_history
        )

            graph: CompiledStateGraph = create_multi_agent_graph()

            try:
                final_state = graph.invoke(initial_state)
            except Exception as e:
                logger.error(f"图执行失败: {e}", exc_info=True)
                initial_state["error_message"] = f"执行失败: {str(e)}"
                final_state = initial_state

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
                "execution_result": (
                    final_state.get("execution_result").model_dump()
                    if final_state.get("execution_result")
                    else None
                ),
                "sql_execution_result": final_state.get("sql_execution_result"),
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
