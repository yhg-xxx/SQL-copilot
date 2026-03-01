import logging
import json
from typing import Dict, List, Any
import mysql.connector
from mysql.connector import Error as MySQLError

from langchain_core.messages import SystemMessage, HumanMessage

from app.multi_agent.state.agent_state import AgentState, ValidationResult
from app.utils.llm_util import get_llm

logger = logging.getLogger(__name__)


def validate_sql_with_mysql(state: AgentState, datasource_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    使用 MySQL 直接验证 SQL 语法正确性
    注意：此函数仅验证 SELECT 查询语句，其他类型 SQL 直接返回错误

    Args:
        state: 智能体状态
        datasource_config: 数据源连接配置

    Returns:
        验证结果字典
    """
    result = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "mysql_validation_passed": False,
        "mysql_explain_result": None
    }

    try:
        sql_query = state.get("generated_sql", "")
        if not sql_query:
            result["errors"].append("SQL 语句为空")
            return result

        # 只处理 SELECT 查询语句
        sql_upper = sql_query.upper().strip()
        logger.info(f"SQL 类型判断: {sql_upper[:50]}...")

        # 检查是否为 SELECT 语句
        # if not sql_upper.startswith("SELECT"):
        #     error_msg = f"仅支持 SELECT 查询语句验证，当前语句类型为: {sql_upper.split()[0] if sql_upper else '未知'}"
        #     logger.error(error_msg)
        #     result["errors"].append(error_msg)
        #     return result

        # 检查必要的配置项
        required_fields = ["host", "username", "password", "database"]
        missing_fields = [field for field in required_fields if not datasource_config.get(field)]

        if missing_fields:
            result["warnings"].append(f"数据源配置缺少必要字段: {missing_fields}")
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
                connection_timeout=10,
                autocommit=False
            )
            logger.info(
                f"MySQL 连接成功: {datasource_config.get('host')}:{datasource_config.get('port', 3306)}/{datasource_config.get('database')}")
        except Exception as e:
            logger.error(f"MySQL 连接失败: {e}")
            result["errors"].append(f"MySQL 连接失败: {str(e)}")
            return result

        cursor = None
        try:
            # 创建游标，使用缓冲游标避免 Unread result found 错误
            cursor = connection.cursor(buffered=True)
            logger.info("MySQL 游标创建成功")

            # 1. 尝试执行 EXPLAIN 验证语法和执行计划
            try:
                # 清理 SQL 语句，移除可能的多余分号
                clean_sql = sql_query.strip().rstrip(';')
                explain_sql = f"EXPLAIN {clean_sql}"
                logger.info(f"执行 EXPLAIN 语句: {explain_sql}")

                cursor.execute(explain_sql)
                explain_result = cursor.fetchall()
                # EXPLAIN是 MySQL 自带的 SQL 分析命令，
                # 可以识别：语法错误、不存在的表、不存在的字段、索引使用情况等

                # 打印 EXPLAIN 结果
                logger.info("EXPLAIN 结果详情:")
                logger.info(f"结果行数: {len(explain_result)}")

                if cursor.description:
                    # 获取列名
                    columns = [desc[0] for desc in cursor.description]
                    logger.info(f"EXPLAIN 列名: {columns}")

                for i, row in enumerate(explain_result):
                    logger.info(f"行 {i}: {row}")

                result["mysql_explain_result"] = str(explain_result)
                logger.info("EXPLAIN 执行成功")

            except MySQLError as e:
                logger.error(f"EXPLAIN 执行失败: {e}")
                result["errors"].append(f"EXPLAIN 执行失败: {str(e)}")
                return result

            # 确保所有结果都被读取
            if cursor.with_rows:
                remaining = cursor.fetchall()
                if remaining:
                    logger.warning(f"EXPLAIN 有未读取的结果: {remaining}")

            # 2. 执行 SELECT 查询验证
            logger.info("开始 SELECT 查询语句验证")

            # 对于 SELECT 查询，使用 LIMIT 10 验证
            clean_sql = sql_query.rstrip(';').strip()

            # 检查是否已有 LIMIT 子句
            if "LIMIT" not in sql_upper:
                validation_sql = f"{clean_sql} LIMIT 10"
                logger.info(f"添加 LIMIT 10 进行验证")
            else:
                validation_sql = clean_sql
                logger.info(f"已存在 LIMIT 子句，使用原 SQL")

            try:
                logger.info(f"执行 SELECT 验证: {validation_sql}")
                cursor.execute(validation_sql)

                # 打印查询信息
                logger.info(f"SELECT 验证执行成功")
                logger.info(f"影响行数: {cursor.rowcount}")

                # 打印列信息
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    logger.info(f"查询列: {columns}")

                # 读取所有结果
                if cursor.with_rows:
                    results = cursor.fetchall()
                    logger.info(f"查询结果行数: {len(results)}")

                    # 打印前几行结果
                    if results:
                        logger.info("查询结果示例 (前5行):")
                        for i, row in enumerate(results[:5]):
                            logger.info(f"  行 {i}: {row}")
                    else:
                        logger.info("查询结果为空")

                result["mysql_validation_passed"] = True
                result["warnings"].append("MySQL SELECT 语法验证通过")
                logger.info("SELECT 语法验证通过")

            except MySQLError as e:
                logger.error(f"SELECT 语法验证失败: {e}")
                result["errors"].append(f"SELECT 语法验证失败: {str(e)}")
                result["mysql_validation_passed"] = False

        except MySQLError as e:
            logger.error(f"MySQL 验证失败: {e}")
            result["errors"].append(f"MySQL 验证失败: {str(e)}")
        except Exception as e:
            logger.error(f"MySQL 验证过程异常: {e}", exc_info=True)
            result["errors"].append(f"MySQL 验证过程异常: {str(e)}")
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
        result["errors"].append(f"MySQL 连接失败: {str(e)}")
    except Exception as e:
        logger.error(f"MySQL 验证过程异常: {e}", exc_info=True)
        result["errors"].append(f"MySQL 验证过程异常: {str(e)}")

    # 输出最终验证结果
    result["valid"] = len(result["errors"]) == 0 and result["mysql_validation_passed"]
    logger.info(
        f"MySQL 验证最终结果: valid={result['valid']}, mysql_validation_passed={result['mysql_validation_passed']}, errors={result['errors']}")

    return result


def validate_sql_with_llm(state: AgentState, datasource_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    使用大模型验证 SQL 的正确性和合理性

    Args:
        state: 智能体状态
        datasource_schema: 数据库表结构信息

    Returns:
        验证结果字典
    """
    result = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "llm_validation_passed": False,
        "llm_feedback": ""
    }

    try:
        sql_query = state.get("generated_sql", "")
        user_query = state.get("user_query", "")

        if not sql_query:
            result["errors"].append("SQL 语句为空")
            return result

        # 准备提示词
        schema_text = ""
        if datasource_schema:
            schema_text = "数据库表结构信息:\n"
            for table_name, table_info in datasource_schema.items():
                schema_text += f"\n表: {table_name}"
                if table_info.get('comment'):
                    schema_text += f" ({table_info['comment']})"
                schema_text += "\n字段:"
                for field in table_info.get('fields', []):
                    field_desc = f"  - {field['name']} ({field['type']})"
                    if field.get('comment'):
                        field_desc += f": {field['comment']}"
                    schema_text += f"\n{field_desc}"

        system_prompt = f"""你是一个专业的 SQL 验证专家。请验证给定的 SQL 语句是否符合以下标准：

{schema_text}

验证标准：
1. 语法正确性：SQL 语法是否正确
2. 表名正确性：引用的表名是否存在
3. 字段正确性：引用的字段名是否正确
4. 逻辑合理性：SQL 是否合理满足用户需求
5. 性能提示：是否存在潜在的性能问题

用户查询需求：{user_query}

请只返回 JSON 格式的验证结果，不要包含其他文字。

JSON 格式：
{{
  "valid": true/false,
  "llm_validation_passed": true/false,
  "errors": ["错误信息1", "错误信息2"],
  "warnings": ["警告信息1", "警告信息2"],
  "llm_feedback": "详细的验证反馈和建议"
}}

如果 SQL 基本正确但有改进空间，请设置 valid=true 但在 warnings 中给出建议。
如果 SQL 存在严重错误，请设置 valid=false 并在 errors 中说明原因。"""

        user_prompt = f"请验证以下 SQL 语句：\n```sql\n{sql_query}\n```"

        # 调用 LLM
        llm = get_llm(temperature=0.0)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        response = llm.invoke(messages)
        response_content = response.content.strip()

        # 清理响应
        if "```json" in response_content:
            response_content = response_content.split("```json")[1]
        if "```" in response_content:
            response_content = response_content.split("```")[0]
        response_content = response_content.strip()

        # 解析 LLM 验证结果
        try:
            llm_result = json.loads(response_content)
            result.update(llm_result)
        except json.JSONDecodeError:
            # 尝试处理可能的格式问题
            try:
                # 移除可能的 markdown 代码块标记
                if response_content.startswith("```"):
                    lines = response_content.split('\n')
                    if lines[0].startswith("```"):
                        response_content = '\n'.join(lines[1:-1])

                # 再次尝试解析
                llm_result = json.loads(response_content)
                result.update(llm_result)
            except:
                result["errors"].append("LLM 返回格式错误")
                result["llm_feedback"] = f"无法解析的响应: {response_content[:100]}..."

    except Exception as e:
        result["errors"].append(f"LLM 验证过程异常: {str(e)}")

    return result


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

            # 调试：打印数据源可用属性
            datasource_attrs = {attr: getattr(datasource, attr, 'N/A')
                                for attr in
                                ['id', 'name', 'configuration', 'config', 'host', 'port', 'username', 'password',
                                 'database']
                                if hasattr(datasource, attr)}
            logger.info(f"数据源 {datasource_id} 属性: {datasource_attrs}")

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
                # 检查是否有单独的字段
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


def syntax_validator(state: AgentState) -> AgentState:
    """
    语法验证智能体：负责验证 SQL 语法和字段表名正确性
    使用 LLM 统一进行修复

    Args:
        state: 智能体状态

    Returns:
        更新后的状态
    """
    logger.info("语法验证智能体开始工作")

    # 获取修复尝试次数
    fix_attempts = state.get("fix_attempts", 0)
    max_fix_attempts = 3  # 最大修复尝试次数

    try:
        generated_sql = state.get("generated_sql", "")
        datasource_id = state.get("datasource_id")
        user_query = state.get("user_query", "")

        # 添加调试信息
        logger.info(f"开始验证 SQL: {generated_sql}")
        logger.info(f"数据源ID: {datasource_id}")
        logger.info(f"当前修复尝试次数: {fix_attempts}")

        if not generated_sql or generated_sql == "No SQL query generated":
            validation_result = ValidationResult(
                valid=False,
                errors=["没有可验证的 SQL"],
                warnings=[],
                mysql_validation_passed=False,
                llm_validation_passed=False,
                mysql_explain_result=None,
                llm_feedback=""
            )
            state["validation_result"] = validation_result
            state["error_message"] = "没有可验证的 SQL"
            return state

        # 获取数据库表结构信息 - 优先使用 state 中的 db_info，避免重复获取
        datasource_schema = state.get("db_info", {})
        
        # 如果 state 中没有 db_info，再从数据库获取（备用方案）
        if not datasource_schema and datasource_id:
            try:
                from .sql_generator import get_datasource_schema
                datasource_schema = get_datasource_schema(datasource_id)
                logger.info(f"从数据库获取到数据源表结构，表数量: {len(datasource_schema)}")
            except ImportError as e:
                logger.warning(f"无法导入 get_datasource_schema: {e}")
                datasource_schema = {}
        elif datasource_schema:
            logger.info(f"使用 state 中的数据源表结构，表数量: {len(datasource_schema)}")

        # 验证循环（最多尝试修复 max_fix_attempts 次）
        for attempt in range(fix_attempts, max_fix_attempts + 1):
            logger.info(f"验证尝试 {attempt + 1}/{max_fix_attempts + 1}")

            # 初始化验证结果
            all_errors = []
            all_warnings = []
            mysql_validation_passed = False
            llm_validation_passed = False
            mysql_explain_result = None
            llm_feedback = ""

            # 1. MySQL 直接验证
            mysql_result = {}
            if datasource_id:
                try:
                    datasource_config = get_datasource_config(datasource_id)
                    logger.info(f"获取到的数据源配置: {datasource_config}")

                    if datasource_config:
                        required_config_fields = ["host", "username", "password", "database"]
                        missing_fields = [field for field in required_config_fields
                                          if not datasource_config.get(field)]

                        if missing_fields:
                            warning_msg = f"数据源配置不完整，缺少字段: {missing_fields}，跳过 MySQL 验证"
                            all_warnings.append(warning_msg)
                            logger.warning(warning_msg)
                        else:
                            # 创建临时状态进行验证
                            temp_state = state.copy()
                            temp_state["generated_sql"] = generated_sql

                            mysql_result = validate_sql_with_mysql(temp_state, datasource_config)
                            all_errors.extend(mysql_result.get("errors", []))
                            all_warnings.extend(mysql_result.get("warnings", []))
                            mysql_validation_passed = mysql_result.get("mysql_validation_passed", False)
                            mysql_explain_result = mysql_result.get("mysql_explain_result")
                            logger.info(f"MySQL 验证结果: {'通过' if mysql_validation_passed else '失败'}")

                            if mysql_result.get("errors"):
                                logger.error(f"MySQL 验证错误: {mysql_result.get('errors')}")
                    else:
                        warning_msg = "无法获取数据源配置，跳过 MySQL 验证"
                        all_warnings.append(warning_msg)
                        logger.warning(warning_msg)
                except Exception as e:
                    error_msg = f"MySQL 验证异常: {str(e)}"
                    all_warnings.append(error_msg)
                    logger.error(error_msg, exc_info=True)
            else:
                warning_msg = "无数据源ID，跳过 MySQL 验证"
                all_warnings.append(warning_msg)
                logger.warning(warning_msg)

            # 2. LLM 语义验证
            llm_result = {}
            try:
                # 创建包含当前 generated_sql 的状态用于验证
                current_state = state.copy()
                current_state["generated_sql"] = generated_sql

                llm_result = validate_sql_with_llm(current_state, datasource_schema)
                all_errors.extend(llm_result.get("errors", []))
                all_warnings.extend(llm_result.get("warnings", []))
                llm_validation_passed = llm_result.get("llm_validation_passed", False)
                llm_feedback = llm_result.get("llm_feedback", "")
                logger.info(f"LLM 验证结果: {'通过' if llm_validation_passed else '失败'}")

            except Exception as e:
                error_msg = f"LLM 验证异常: {str(e)}"
                all_errors.append(error_msg)
                logger.error(error_msg, exc_info=True)

            # 判断是否需要修复
            need_fix = len(all_errors) > 0 and attempt < max_fix_attempts

            if not need_fix:
                # 验证通过或达到最大尝试次数
                is_valid = llm_validation_passed and len(all_errors) == 0

                if len(all_errors) == 0 and len(all_warnings) > 0:
                    is_valid = True

                # 记录修复历史
                if fix_attempts > 0:
                    state["was_fixed"] = True
                    state["fix_attempts"] = fix_attempts

                validation_result = ValidationResult(
                    valid=is_valid,
                    errors=all_errors,
                    warnings=all_warnings,
                    mysql_validation_passed=mysql_validation_passed,
                    llm_validation_passed=llm_validation_passed,
                    mysql_explain_result=mysql_explain_result,
                    llm_feedback=llm_feedback
                )

                state["validation_result"] = validation_result
                state["generated_sql"] = generated_sql  # 确保最终 SQL 被保存

                if is_valid:
                    logger.info(f"SQL 语法验证通过 (修复尝试: {fix_attempts}次)")
                    if all_warnings:
                        logger.warning(f"验证警告: {all_warnings}")
                else:
                    logger.error(f"SQL 语法验证失败，已尝试修复 {fix_attempts} 次: {all_errors}")

                break
            else:
                # 需要尝试修复
                logger.info(f"验证失败，尝试修复 (第 {attempt + 1} 次尝试)")

                # 使用 LLM 进行智能修复
                logger.info("使用 LLM 进行智能修复")
                llm_fixed_sql = llm_based_fix(generated_sql, all_errors, user_query, datasource_schema)

                if llm_fixed_sql and llm_fixed_sql != generated_sql:
                    # 修复成功，更新 SQL 并继续验证
                    state["generated_sql"] = llm_fixed_sql
                    state["fix_attempts"] = attempt + 1
                    state["fix_explanation"] = f"使用 LLM 进行智能修复，修正了 {len(all_errors)} 个错误"
                    generated_sql = llm_fixed_sql

                    logger.info(f"LLM 修复成功，新 SQL: {llm_fixed_sql}")
                    logger.info(f"继续验证修复后的 SQL...")

                    # 继续下一轮验证
                    continue
                else:
                    # 无法修复
                    logger.warning("LLM 修复失败或无变化")

                    # 无法修复或达到最大尝试次数
                    logger.warning(f"无法修复错误或达到最大尝试次数: {all_errors}")

                    validation_result = ValidationResult(
                        valid=False,
                        errors=all_errors,
                        warnings=all_warnings,
                        mysql_validation_passed=mysql_validation_passed,
                        llm_validation_passed=llm_validation_passed,
                        mysql_explain_result=mysql_explain_result,
                        llm_feedback=llm_feedback
                    )

                    state["validation_result"] = validation_result
                    state["error_message"] = f"SQL 验证失败，已尝试修复 {attempt + 1} 次"
                    break

    except Exception as e:
        logger.error(f"语法验证过程中发生错误: {e}", exc_info=True)
        validation_result = ValidationResult(
            valid=False,
            errors=[f"验证过程出错: {str(e)}"],
            warnings=[],
            mysql_validation_passed=False,
            llm_validation_passed=False,
            mysql_explain_result=None,
            llm_feedback=""
        )
        state["validation_result"] = validation_result
        state["error_message"] = f"语法验证失败: {str(e)}"

    return state


def llm_based_fix(sql: str, errors: List[str], user_query: str, datasource_schema: Dict[str, Any] = None) -> str:
    """
    使用 LLM 进行智能修复

    Args:
        sql: 原始 SQL
        errors: 错误信息列表
        user_query: 用户原始查询
        datasource_schema: 数据库表结构信息

    Returns:
        修复后的 SQL，如果无法修复返回 None
    """
    try:
        logger.info("使用 LLM 进行智能修复")

        # 准备表结构信息
        schema_text = ""
        if datasource_schema:
            schema_text = "数据库表结构信息:\n"
            for table_name, table_info in datasource_schema.items():
                schema_text += f"\n表: {table_name}"
                if table_info.get('comment'):
                    schema_text += f" ({table_info['comment']})"
                schema_text += "\n字段:"
                for field in table_info.get('fields', []):
                    field_desc = f"  - {field['name']} ({field['type']})"
                    if field.get('comment'):
                        field_desc += f": {field['comment']}"
                    schema_text += f"\n{field_desc}"

        system_prompt = f"""你是一个专业的 SQL 修复专家。请根据以下信息修复有问题的 SQL 语句：

{schema_text}

错误信息:
{chr(10).join(f'- {error}' for error in errors)}

用户原始查询: {user_query}

请修复以下 SQL 语句中的错误，只返回修复后的 SQL 语句，不要包含其他解释或文字。

原 SQL:sql
{sql}
        修复后的 SQL:"""

        # 调用 LLM
        llm = get_llm(temperature=0.1)  # 较低温度以获得更确定的修复
        messages = [
            SystemMessage(content=system_prompt),
        ]

        response = llm.invoke(messages)
        response_content = response.content.strip()

        # 提取 SQL
        if "```sql" in response_content:
            response_content = response_content.split("```sql")[1]
        if "```" in response_content:
            response_content = response_content.split("```")[0]

        fixed_sql = response_content.strip()

        if fixed_sql and fixed_sql != sql:
            logger.info(f"LLM 修复成功: {fixed_sql}")
            return fixed_sql
        else:
            logger.warning("LLM 修复失败或无变化")
            return None

    except Exception as e:
        logger.error(f"LLM 修复过程中发生错误: {e}", exc_info=True)
        return None