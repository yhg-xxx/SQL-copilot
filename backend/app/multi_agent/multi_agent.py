import logging
import asyncio
from typing import Any, AsyncGenerator
from langgraph.graph.state import CompiledStateGraph
from app.multi_agent.analysis.graph import create_multi_agent_graph
from app.multi_agent.state.agent_state import AgentState, ValidationResult, OptimizationResult, ExecutionResult, \
    SummaryResult

logger = logging.getLogger(__name__)

# 步骤名称映射
STEP_NAMES = {
    "database_selector": "数据库选择",
    "sql_generator": "SQL 生成",
    "syntax_validator": "语法验证",
    "execution_optimizer": "执行优化",
    "sql_executor": "SQL 执行",
    "summary_generator": "总结中"
}

class MultiAgent:
    """
    多智能体协作系统主类
    """
    

    def __init__(self):
        self.running_tasks = {}
        self.step_start_times = {}
        self.step_progress_ids = {}

    @staticmethod
    async def run_agent(
            query: str,
            chat_id: str = None,
            user_id: int = 1,
            datasource_id: int = None,
    ) -> dict[str, None | str | dict | ValidationResult | OptimizationResult | ExecutionResult | dict[str, Any] | int |
                   list[dict[str, Any]] | SummaryResult | bool | Any] | None:
        """
        运行多智能体系统

        Args:
            query: 用户输入的自然语言查询
            chat_id: 会话ID
            user_id: 用户ID
            datasource_id: 数据源ID

        Returns:
            包含最终结果的字典
        """
        logger.info(f"多智能体系统启动，查询: {query}")

        try:
            logger.info(f"当前用户ID: {user_id}")
        except Exception as e:
            logger.error(f"记录用户ID时出错: {e}")

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

                    # 格式化历史记录 - 只保留最近 5 轮
                    formatted_history = []
                    for record in history:
                        if record.question:
                            formatted_history.append({
                                "role": "user",
                                "content": record.question,
                                "timestamp": record.create_time
                            })
                        if record.sql_statement:
                            formatted_history.append({
                                "role": "assistant",
                                "content": record.sql_statement,
                                "timestamp": record.create_time,
                                "sql": record.sql_statement
                            })
                    
                    # 只保留最近 5 轮对话（10 条记录）
                    chat_history = formatted_history[-10:] if len(formatted_history) > 10 else formatted_history
                    logger.info(f"获取到 {len(chat_history)} 条对话历史记录（最近 5 轮）")
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"获取对话历史失败: {e}")

        # 初始化状态 - 确保始终执行
        initial_state = AgentState(
            user_query=query,
            fix_attempts=0,
            datasource_id=datasource_id,
            user_id=user_id,
            chat_history=chat_history
        )

        logger.info(f"初始状态创建成功: {initial_state}")

        graph: CompiledStateGraph = create_multi_agent_graph()

        try:
            final_state = await graph.ainvoke(initial_state)
        except Exception as e:
            logger.error(f"图执行失败: {e}", exc_info=True)
            initial_state["error_message"] = f"执行失败: {str(e)}"
            final_state = initial_state

        result = {
            "success": final_state.get("error_message") is None,
            "user_query": query,
            "generated_sql": final_state.get("generated_sql"),
            "validated_sql": final_state.get("validated_sql"),  # 验证成功但未优化的SQL
            "retrieved_examples": final_state.get("retrieved_examples"),  # RAG检索到的历史示例
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

    @staticmethod
    async def run_agent_stream(
            query: str,
            chat_id: str = None,
            user_id: int = 1,
            datasource_id: int = None,
    ) -> AsyncGenerator[dict, None]:
        """
        流式运行多智能体系统，实时返回每个步骤的进度

        Args:
            query: 用户输入的自然语言查询
            chat_id: 会话ID
            user_id: 用户ID
            datasource_id: 数据源ID

        Yields:
            包含步骤进度或最终结果的字典
        """
        logger.info(f"多智能体系统流式启动，查询: {query}")

        # 获取对话历史
        chat_history = []
        if chat_id:
            try:
                from app.database.db import SessionLocal
                from app.models.user_qa_record import UserQARecord
                db = SessionLocal()
                try:
                    history = db.query(UserQARecord).filter(
                        UserQARecord.conversation_id == chat_id
                    ).order_by(UserQARecord.create_time.asc()).all()

                    formatted_history = []
                    for record in history:
                        if record.question:
                            formatted_history.append({
                                "role": "user",
                                "content": record.question,
                                "timestamp": record.create_time
                            })
                        if record.sql_statement:
                            formatted_history.append({
                                "role": "assistant",
                                "content": record.sql_statement,
                                "timestamp": record.create_time,
                                "sql": record.sql_statement
                            })
                    
                    chat_history = formatted_history[-10:] if len(formatted_history) > 10 else formatted_history
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"获取对话历史失败: {e}")

        # 初始化状态
        initial_state = AgentState(
            user_query=query,
            fix_attempts=0,
            datasource_id=datasource_id,
            user_id=user_id,
            chat_history=chat_history
        )

        graph: CompiledStateGraph = create_multi_agent_graph()
        final_state = initial_state

        # 定义步骤执行顺序（按预期执行顺序）
        step_order = ["database_selector", "sql_generator", "syntax_validator", "execution_optimizer", "sql_executor"]
        sent_steps = set()
        actual_executed_nodes = []

        try:
            # 首先立即发送第一个步骤，让用户知道已经开始
            first_step = step_order[0]
            if first_step in STEP_NAMES and first_step not in sent_steps:
                step_name = STEP_NAMES[first_step]
                logger.info(f"发送步骤进度: {step_name}")
                yield {
                    "type": "step",
                    "step": step_name,
                    "node": first_step
                }
                sent_steps.add(first_step)
                await asyncio.sleep(0.1)

            # 使用 astream 流式执行，获取每个步骤的进度
            async for event in graph.astream(initial_state, stream_mode="updates"):
                # event 格式: {node_name: state_update}
                for node_name, state_update in event.items():
                    actual_executed_nodes.append(node_name)
                    
                    # 找到当前步骤在顺序中的位置
                    if node_name in step_order:
                        current_idx = step_order.index(node_name)
                        # 发送下一个步骤（如果存在且未发送）
                        next_idx = current_idx + 1
                        if next_idx < len(step_order):
                            next_step = step_order[next_idx]
                            if next_step in STEP_NAMES and next_step not in sent_steps:
                                step_name = STEP_NAMES[next_step]
                                logger.info(f"发送步骤进度: {step_name}")
                                yield {
                                    "type": "step",
                                    "step": step_name,
                                    "node": next_step
                                }
                                sent_steps.add(next_step)
                                await asyncio.sleep(0.1)
                    
                    # 更新最终状态
                    if isinstance(state_update, dict):
                        final_state = {**final_state, **state_update}
        except Exception as e:
            logger.error(f"图执行失败: {e}", exc_info=True)
            final_state["error_message"] = f"执行失败: {str(e)}"

        # 构建最终结果
        result = {
            "type": "result",
            "success": final_state.get("error_message") is None,
            "user_query": query,
            "generated_sql": final_state.get("generated_sql"),
            "validated_sql": final_state.get("validated_sql"),
            "retrieved_examples": final_state.get("retrieved_examples"),
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

        logger.info(f"多智能体系统流式执行完成")
        yield result