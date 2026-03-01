import logging
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.multi_agent.state.agent_state import AgentState
from app.multi_agent.agents.sql_generator import sql_generator
from app.multi_agent.agents.syntax_validator import syntax_validator
from app.multi_agent.agents.execution_optimizer import execution_optimizer
from app.multi_agent.agents.sql_executor import sql_executor

logger = logging.getLogger(__name__)


def should_continue_after_validation(state: AgentState) -> str:
    """
    验证后的条件判断：如果验证失败则结束，否则继续优化

    Args:
        state: 智能体状态

    Returns:
        下一个节点名称
    """
    validation_result = state.get("validation_result")

    if validation_result and not validation_result.valid:
        logger.warning("SQL 验证失败，结束流程")
        return "end"

    return "execution_optimizer"


def create_multi_agent_graph():
    """
    创建多智能体协作图

    Returns:
        编译后的 LangGraph
    """
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("sql_generator", sql_generator)
    graph.add_node("syntax_validator", syntax_validator)
    graph.add_node("execution_optimizer", execution_optimizer)
    graph.add_node("sql_executor", sql_executor)

    # 设置入口点
    graph.set_entry_point("sql_generator")

    # 添加边
    graph.add_edge("sql_generator", "syntax_validator")

    # 添加条件边：验证后决定是否继续优化
    graph.add_conditional_edges(
        "syntax_validator",
        should_continue_after_validation,
        {
            "execution_optimizer": "execution_optimizer",
            "end": END
        }
    )

    # 添加优化器到执行器的边
    graph.add_edge("execution_optimizer", "sql_executor")

    # 添加执行器到结束的边
    graph.add_edge("sql_executor", END)

    # 编译图
    graph_compiled: CompiledStateGraph = graph.compile()
    logger.info("多智能体协作图创建完成")
    return graph_compiled