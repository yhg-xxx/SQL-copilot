import logging
import json
from typing import Dict, List, Any
from .sql_generator import get_datasource_schema
from langchain_core.messages import SystemMessage, HumanMessage

from app.multi_agent.state.agent_state import AgentState, ValidationResult
from app.multi_agent.agents.datasource_utils import get_datasource_config
from app.multi_agent.agents.schema_utils import format_schema_for_prompt
from app.multi_agent.agents.db_verifier_executor import get_db_verifier_executor
from app.utils.llm_util import get_llm

logger = logging.getLogger(__name__)


def validate_sql_with_database(state: AgentState, datasource_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    使用对应数据库验证 SQL 语句

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
        "validation_passed": False,
        "explain_result": None
    }

    try:
        sql_query = state.get("generated_sql", "")
        if not sql_query:
            result["errors"].append("SQL 语句为空")
            return result

        db_type = datasource_config.get("db_type", "mysql")
        logger.info(f"使用数据库类型进行验证: {db_type}")

        verifier_executor = get_db_verifier_executor(db_type, datasource_config)
        verify_result = verifier_executor.validate_sql(sql_query)

        result.update(verify_result)

    except Exception as e:
        logger.error(f"数据库验证过程异常: {e}", exc_info=True)
        result["errors"].append(f"验证过程异常: {str(e)}")

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

        schema_text = format_schema_for_prompt(datasource_schema) if datasource_schema else ""

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

        llm = get_llm(temperature=0.0)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        response = llm.invoke(messages)
        response_content = response.content.strip()

        if "```json" in response_content:
            response_content = response_content.split("```json")[1]
        if "```" in response_content:
            response_content = response_content.split("```")[0]
        response_content = response_content.strip()

        try:
            llm_result = json.loads(response_content)
            result.update(llm_result)
            logger.info(f"LLM 验证结果 - valid: {result.get('valid')}, "
                       f"llm_validation_passed: {result.get('llm_validation_passed')}, "
                       f"errors: {result.get('errors')}, "
                       f"warnings: {result.get('warnings')}, "
                       f"llm_feedback: {result.get('llm_feedback')}")
        except json.JSONDecodeError:
            result["errors"].append("LLM 返回格式错误")
            logger.error(f"LLM 验证结果 - valid: {result.get('valid')}, "
                        f"llm_validation_passed: {result.get('llm_validation_passed')}, "
                        f"errors: {result.get('errors')}, "
                        f"warnings: {result.get('warnings')}, "
                        f"llm_feedback: {result.get('llm_feedback')}")

    except Exception as e:
        result["errors"].append(f"LLM 验证过程异常: {str(e)}")
        logger.error(f"LLM 验证过程异常 - errors: {result.get('errors')}, "
                    f"llm_feedback: {result.get('llm_feedback')}")

    return result


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

    fix_attempts = state.get("fix_attempts", 0)
    max_fix_attempts = 3

    try:
        generated_sql = state.get("generated_sql", "")
        datasource_id = state.get("datasource_id")
        user_query = state.get("user_query", "")

        logger.info(f"开始验证 SQL: {generated_sql}")
        logger.info(f"数据源ID: {datasource_id}")
        logger.info(f"当前修复尝试次数: {fix_attempts}")

        if not generated_sql or generated_sql == "No SQL query generated":
            validation_result = ValidationResult(
                valid=False,
                errors=["SQL语句为空，没有可验证的 SQL"],
                warnings=[],
                mysql_validation_passed=False,
                llm_validation_passed=False,
                mysql_explain_result=None,
                llm_feedback=""
            )
            state["validation_result"] = validation_result
            return state

        datasource_schema = state.get("db_info", {})

        if not datasource_schema and datasource_id:
            try:
                datasource_schema = get_datasource_schema(datasource_id)
                logger.info(f"从数据库获取到数据源表结构，表数量: {len(datasource_schema)}")
            except ImportError as e:
                logger.warning(f"无法导入 get_datasource_schema: {e}")
                datasource_schema = {}
        elif datasource_schema:
            logger.info(f"使用 state 中的数据源表结构，表数量: {len(datasource_schema)}")

        for attempt in range(fix_attempts, max_fix_attempts + 1):
            logger.info(f"验证尝试 {attempt + 1}/{max_fix_attempts + 1}")

            all_errors = []
            all_warnings = []
            validation_passed = False
            llm_validation_passed = False
            explain_result = None
            llm_feedback = ""

            if datasource_id:
                try:
                    datasource_config = get_datasource_config(datasource_id)
                    logger.info(f"获取到的数据源配置: {datasource_config}")

                    if datasource_config:
                        required_config_fields = ["host", "username", "password", "database"]
                        missing_fields = [field for field in required_config_fields
                                          if not datasource_config.get(field)]

                        if missing_fields:
                            warning_msg = f"数据源配置不完整，缺少字段: {missing_fields}，跳过数据库验证"
                            all_warnings.append(warning_msg)
                            logger.warning(warning_msg)
                        else:
                            temp_state = state.copy()
                            temp_state["generated_sql"] = generated_sql

                            db_result = validate_sql_with_database(temp_state, datasource_config)
                            all_errors.extend(db_result.get("errors", []))
                            all_warnings.extend(db_result.get("warnings", []))
                            validation_passed = db_result.get("validation_passed", False)
                            explain_result = db_result.get("explain_result")
                            logger.info(f"数据库验证结果: {'通过' if validation_passed else '失败'}")

                            if db_result.get("errors"):
                                logger.error(f"数据库验证错误: {db_result.get('errors')}")
                    else:
                        warning_msg = "无法获取数据源配置，跳过数据库验证"
                        all_warnings.append(warning_msg)
                        logger.warning(warning_msg)
                except Exception as e:
                    error_msg = f"数据库验证异常: {str(e)}"
                    all_warnings.append(error_msg)
                    logger.error(error_msg, exc_info=True)
            else:
                warning_msg = "无数据源ID，跳过数据库验证"
                all_warnings.append(warning_msg)
                logger.warning(warning_msg)

            try:
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

            need_fix = len(all_errors) > 0 and attempt < max_fix_attempts

            if not need_fix:
                is_valid = llm_validation_passed and len(all_errors) == 0

                if len(all_errors) == 0 and len(all_warnings) > 0:
                    is_valid = True

                if fix_attempts > 0:
                    state["was_fixed"] = True
                    state["fix_attempts"] = fix_attempts

                validation_result = ValidationResult(
                    valid=is_valid,
                    errors=all_errors,
                    warnings=all_warnings,
                    mysql_validation_passed=validation_passed,
                    llm_validation_passed=llm_validation_passed,
                    mysql_explain_result=explain_result,
                    llm_feedback=llm_feedback
                )

                state["validation_result"] = validation_result
                state["generated_sql"] = generated_sql

                if is_valid:
                    logger.info(f"SQL 语法验证通过 (修复尝试: {fix_attempts}次)")
                    if all_warnings:
                        logger.warning(f"验证警告: {all_warnings}")
                else:
                    logger.error(f"SQL 语法验证失败，已尝试修复 {fix_attempts} 次: {all_errors}")

                break
            else:
                logger.info(f"验证失败，尝试修复 (第 {attempt + 1} 次尝试)")

                logger.info("使用 LLM 进行智能修复")
                llm_fixed_sql = llm_based_fix(generated_sql, all_errors, user_query, datasource_schema)

                if llm_fixed_sql and llm_fixed_sql != generated_sql:
                    state["generated_sql"] = llm_fixed_sql
                    state["fix_attempts"] = attempt + 1
                    state["fix_explanation"] = f"使用 LLM 进行智能修复，修正了 {len(all_errors)} 个错误"
                    generated_sql = llm_fixed_sql

                    logger.info(f"LLM 修复成功，新 SQL: {llm_fixed_sql}")
                    logger.info(f"继续验证修复后的 SQL...")

                    continue
                else:
                    logger.warning("LLM 修复失败或无变化")

                    logger.warning(f"无法修复错误或达到最大尝试次数: {all_errors}")

                    validation_result = ValidationResult(
                        valid=False,
                        errors=all_errors,
                        warnings=all_warnings,
                        mysql_validation_passed=validation_passed,
                        llm_validation_passed=llm_validation_passed,
                        mysql_explain_result=explain_result,
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


def llm_based_fix(sql: str, errors: List[str], user_query: str, datasource_schema: Dict[str, Any] = None) -> Any | None:
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

        schema_text = format_schema_for_prompt(datasource_schema) if datasource_schema else ""

        system_prompt = f"""你是一个专业的 SQL 修复专家。请根据以下信息修复有问题的 SQL 语句：

{schema_text}

错误信息:
{chr(10).join(f'- {error}' for error in errors)}

用户原始查询: {user_query}

请修复以下 SQL 语句中的错误，只返回修复后的 SQL 语句，不要包含其他解释或文字。

原 SQL:
{sql}

修复后的 SQL:"""

        llm = get_llm(temperature=0.1)
        messages = [
            SystemMessage(content=system_prompt),
        ]

        response = llm.invoke(messages)
        response_content = response.content.strip()

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
