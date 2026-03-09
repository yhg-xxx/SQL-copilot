import logging
from typing import Dict, Any

from app.multi_agent.state.agent_state import AgentState, ExecutionResult
from app.multi_agent.agents.datasource_utils import get_datasource_config
from app.multi_agent.agents.db_verifier_executor import get_db_verifier_executor

logger = logging.getLogger(__name__)


def execute_sql_with_database(state: AgentState, datasource_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    使用对应数据库执行 SQL 语句

    Args:
        state: 智能体状态
        datasource_config: 数据源连接配置

    Returns:
        执行结果字典
    """
    try:
        final_sql = state.get("final_sql", "")
        if not final_sql:
            return {
                "success": False,
                "data": None,
                "columns": None,
                "row_count": 0,
                "error": "SQL 语句为空"
            }

        db_type = datasource_config.get("db_type", "mysql")
        logger.info(f"使用数据库类型执行 SQL: {db_type}")

        verifier_executor = get_db_verifier_executor(db_type, datasource_config)
        exec_result = verifier_executor.execute_sql(final_sql)

        return exec_result

    except Exception as e:
        logger.error(f"数据库执行过程异常: {e}", exc_info=True)
        return {
            "success": False,
            "data": None,
            "columns": None,
            "row_count": 0,
            "error": f"执行过程异常: {str(e)}"
        }


def sql_executor(state: AgentState) -> AgentState:
    """
    SQL 执行器智能体：负责执行最终 SQL 并返回结果
    不调用大模型，纯数据库操作

    Args:
        state: 智能体状态

    Returns:
        更新后的状态
    """
    logger.info("SQL 执行器智能体开始工作")

    try:
        final_sql = state.get("final_sql", "")
        datasource_id = state.get("datasource_id")

        if not final_sql:
            execution_result = ExecutionResult(
                success=False,
                error="没有可执行的 SQL"
            )
            state["execution_result"] = execution_result
            state["error_message"] = "没有可执行的 SQL"
            return state

        datasource_config = {}
        if datasource_id:
            # 首先检查 state 中是否已有缓存的 datasource_config
            datasource_config = state.get("datasource_config")
            
            if datasource_config is None:
                # 如果没有缓存，从数据库获取并保存到 state
                datasource_config = get_datasource_config(datasource_id)
                state["datasource_config"] = datasource_config
                logger.info(f"从数据库获取数据源配置并缓存: {datasource_config}")
            else:
                logger.info(f"使用缓存的数据源配置: {datasource_config}")

        if datasource_config:
            required_config_fields = ["host", "username", "password", "database"]
            missing_fields = [field for field in required_config_fields
                              if not datasource_config.get(field)]

            if missing_fields:
                error_msg = f"数据源配置不完整，缺少字段: {missing_fields}，无法执行 SQL"
                logger.error(error_msg)
                execution_result = ExecutionResult(
                    success=False,
                    error=error_msg
                )
                state["execution_result"] = execution_result
                state["error_message"] = error_msg
                return state

            exec_result = execute_sql_with_database(state, datasource_config)

            if exec_result.get("success"):
                execution_result = ExecutionResult(
                    success=True,
                    data=exec_result.get("data"),
                    columns=exec_result.get("columns"),
                    row_count=exec_result.get("row_count")
                )
                state["execution_result"] = execution_result

                state["sql_execution_result"] = {
                    "columns": exec_result.get("columns"),
                    "data": exec_result.get("data"),
                    "row_count": exec_result.get("row_count")
                }

                logger.info(f"SQL 执行成功，返回 {exec_result.get('row_count')} 条记录")
            else:
                execution_result = ExecutionResult(
                    success=False,
                    error=exec_result.get("error")
                )
                state["execution_result"] = execution_result
                state["error_message"] = exec_result.get("error")
                logger.error(f"SQL 执行失败: {exec_result.get('error')}")
        else:
            error_msg = "无法获取数据源配置，无法执行 SQL"
            logger.error(error_msg)
            execution_result = ExecutionResult(
                success=False,
                error=error_msg
            )
            state["execution_result"] = execution_result
            state["error_message"] = error_msg

    except Exception as e:
        logger.error(f"SQL 执行过程中发生错误: {e}", exc_info=True)
        execution_result = ExecutionResult(
            success=False,
            error=f"执行过程出错: {str(e)}"
        )
        state["execution_result"] = execution_result
        state["error_message"] = f"SQL 执行失败: {str(e)}"

    return state
