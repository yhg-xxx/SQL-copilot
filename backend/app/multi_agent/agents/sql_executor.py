import logging
import json
from typing import Dict, Any
import mysql.connector
from mysql.connector import Error as MySQLError

from app.multi_agent.state.agent_state import AgentState, ExecutionResult

logger = logging.getLogger(__name__)


def get_datasource_config(datasource_id: int) -> Dict[str, Any]:
    """
    获取数据源的连接配置

    Args:
        datasource_id: 数据源ID

    Returns:
        连接配置字典
    """
    try:
        from app.database.db import SessionLocal
        db = SessionLocal()

        try:
            from app.models.datasource import Datasource
            datasource = db.query(Datasource).filter(Datasource.id == datasource_id).first()

            if not datasource:
                logger.warning(f"未找到数据源: {datasource_id}")
                return {}

            # 尝试从不同的属性获取配置信息
            config = {}

            # 首先检查是否有 configuration 属性
            if hasattr(datasource, 'configuration') and datasource.configuration:
                try:
                    config_str = str(datasource.configuration)
                    logger.info(f"configuration 字段原始值: {config_str[:200]}")
                    if config_str:
                        config = json.loads(config_str)
                except json.JSONDecodeError as e:
                    logger.warning(f"解析 configuration 失败: {e}")
                except Exception as e:
                    logger.warning(f"处理 configuration 异常: {e}")

            # 如果没有从 configuration 获取到，尝试其他可能的位置
            if not config and hasattr(datasource, 'config') and datasource.config:
                try:
                    config_str = str(datasource.config)
                    logger.info(f"config 字段原始值: {config_str[:200]}")
                    if config_str:
                        config = json.loads(config_str)
                except (json.JSONDecodeError, AttributeError) as e:
                    logger.warning(f"解析 config 失败: {e}")

            # 如果都没有，尝试获取单独的字段
            if not config:
                for field in ['host', 'port', 'username', 'password', 'database']:
                    if hasattr(datasource, field):
                        value = getattr(datasource, field)
                        if value:
                            config[field] = value

            logger.info(f"解析后的配置字典: {config}")

            # 构建连接配置
            connection_config = {
                "host": config.get("host"),
                "port": config.get("port", 3306),
                "username": config.get("username"),
                "password": config.get("password"),
                "database": config.get("database")
            }

            # 检查必要字段
            required_fields = ["host", "username", "password", "database"]
            missing_fields = [field for field in required_fields if not connection_config.get(field)]

            if missing_fields:
                logger.warning(f"数据源 {datasource_id} 缺少必要字段: {missing_fields}")
                logger.warning(f"当前配置: {connection_config}")

            return connection_config

        finally:
            db.close()

    except Exception as e:
        logger.error(f"获取数据源配置失败: {e}", exc_info=True)
        return {}


def execute_sql_with_mysql(state: AgentState, datasource_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    使用 MySQL 执行 SQL 语句并返回结果

    Args:
        state: 智能体状态
        datasource_config: 数据源连接配置

    Returns:
        执行结果字典
    """
    result = {
        "success": False,
        "data": None,
        "columns": None,
        "row_count": 0,
        "error": None
    }

    try:
        final_sql = state.get("final_sql", "")
        if not final_sql:
            result["error"] = "SQL 语句为空"
            return result

        # 只处理 SELECT 查询语句
        sql_upper = final_sql.upper().strip()
        logger.info(f"SQL 类型判断: {sql_upper[:50]}...")

        # 检查必要的配置项
        required_fields = ["host", "username", "password", "database"]
        missing_fields = [field for field in required_fields if not datasource_config.get(field)]

        if missing_fields:
            result["error"] = f"数据源配置缺少必要字段: {missing_fields}"
            return result

        # 打印连接配置信息（隐藏密码）
        safe_config = datasource_config.copy()
        if safe_config.get("password"):
            safe_config["password"] = "***"
        logger.info(f"MySQL 连接配置: {safe_config}")

        # 建立数据库连接
        try:
            connection = mysql.connector.connect(
                host=datasource_config.get("host"),
                port=datasource_config.get("port", 3306),
                user=datasource_config.get("username"),
                password=datasource_config.get("password"),
                database=datasource_config.get("database"),
                connection_timeout=30,
                autocommit=False
            )
            logger.info(
                f"MySQL 连接成功: {datasource_config.get('host')}:{datasource_config.get('port', 3306)}/{datasource_config.get('database')}")
        except Exception as e:
            logger.error(f"MySQL 连接失败: {e}")
            result["error"] = f"MySQL 连接失败: {str(e)}"
            return result

        cursor = None
        try:
            # 创建游标，使用缓冲游标
            cursor = connection.cursor(buffered=True, dictionary=True)
            logger.info("MySQL 游标创建成功")

            # 清理 SQL 语句，移除注释和多余分号
            clean_sql = final_sql.strip().rstrip(';')

            # 对于 SELECT 查询，使用 LIMIT 1000 限制返回结果数量
            if "LIMIT" not in sql_upper:
                execution_sql = f"{clean_sql} LIMIT 1000"
                logger.info(f"添加 LIMIT 1000 限制结果数量")
            else:
                execution_sql = clean_sql
                logger.info(f"已存在 LIMIT 子句，使用原 SQL")

            try:
                logger.info(f"执行 SQL: {execution_sql}")
                cursor.execute(execution_sql)

                # 获取列信息
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    result["columns"] = columns
                    logger.info(f"查询列: {columns}")

                # 读取所有结果
                if cursor.with_rows:
                    data = cursor.fetchall()
                    result["data"] = data
                    result["row_count"] = len(data)
                    logger.info(f"查询结果行数: {len(data)}")

                    # 打印前几行结果
                    if data:
                        logger.info("查询结果示例 (前5行):")
                        for i, row in enumerate(data[:5]):
                            logger.info(f"  行 {i}: {row}")
                    else:
                        logger.info("查询结果为空")

                result["success"] = True
                logger.info("SQL 执行成功")

            except MySQLError as e:
                logger.error(f"SQL 执行失败: {e}")
                result["error"] = f"SQL 执行失败: {str(e)}"

        except MySQLError as e:
            logger.error(f"MySQL 执行失败: {e}")
            result["error"] = f"MySQL 执行失败: {str(e)}"
        except Exception as e:
            logger.error(f"MySQL 执行过程异常: {e}", exc_info=True)
            result["error"] = f"MySQL 执行过程异常: {str(e)}"
        finally:
            if cursor:
                try:
                    cursor.close()
                    logger.info("MySQL 游标已关闭")
                except Exception as e:
                    logger.error(f"关闭游标时出错: {e}")
            try:
                connection.close()
                logger.info("MySQL 连接已关闭")
            except Exception as e:
                logger.error(f"关闭连接时出错: {e}")

    except mysql.connector.Error as e:
        logger.error(f"MySQL 连接失败: {e}")
        result["error"] = f"MySQL 连接失败: {str(e)}"
    except Exception as e:
        logger.error(f"MySQL 执行过程异常: {e}", exc_info=True)
        result["error"] = f"MySQL 执行过程异常: {str(e)}"

    # 输出最终执行结果
    logger.info(
        f"SQL 执行最终结果: success={result['success']}, row_count={result['row_count']}, error={result['error']}")

    return result


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

        # 获取数据源配置
        datasource_config = {}
        if datasource_id:
            datasource_config = get_datasource_config(datasource_id)
            logger.info(f"获取到的数据源配置: {datasource_config}")

        # 执行 SQL
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

            # 执行 SQL
            exec_result = execute_sql_with_mysql(state, datasource_config)

            if exec_result.get("success"):
                execution_result = ExecutionResult(
                    success=True,
                    data=exec_result.get("data"),
                    columns=exec_result.get("columns"),
                    row_count=exec_result.get("row_count")
                )
                state["execution_result"] = execution_result

                # 同时设置 sql_execution_result 字段（向后兼容）
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
