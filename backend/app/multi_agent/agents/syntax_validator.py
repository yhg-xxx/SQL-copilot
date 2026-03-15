import logging
import json
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from .sql_generator import get_datasource_schema
from .schema_utils import format_schema_for_prompt
from app.multi_agent.state.agent_state import AgentState, ValidationResult
from app.multi_agent.agents.datasource_utils import get_datasource_config

from app.multi_agent.agents.db_verifier_executor import get_db_verifier_executor
from app.utils.llm_util import get_llm
from app.multi_agent.prompts.database_validation_prompts import get_validation_prompt_by_db_type

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


def validate_and_fix_with_llm(
    state: AgentState, 
    schema_text: str, 
    db_type: str
) -> Dict[str, Any]:
    """
    单次验证修复智能体：一次性完成SQL验证和修复

    Args:
        state: 智能体状态
        schema_text: 数据库表结构信息（已格式化）
        db_type: 数据库类型

    Returns:
        验证修复结果字典
    """
    result = {
        "is_valid": False,
        "llm_validation_passed": False,
        "original_sql": "",
        "fixed_sql": "",
        "errors": [],
        "warnings": [],
        "llm_feedback": ""
    }

    try:
        sql_query = state.get("generated_sql", "")
        user_query = state.get("user_query", "")
        db_errors = state.get("db_errors", [])
        result["original_sql"] = sql_query
        result["fixed_sql"] = sql_query

        if not sql_query:
            result["errors"].append("SQL 语句为空")
            return result

        schema_text = schema_text or ""

        db_errors_text = ""
        if db_errors:
            db_errors_text = f"\n\n数据库验证错误（需要修复）：\n" + "\n".join(f"- {error}" for error in db_errors)

        system_prompt = get_validation_prompt_by_db_type(
            db_type=db_type,
            schema_text=schema_text,
            user_query=user_query,
            db_errors_text=db_errors_text
        )

        user_prompt = f"请验证并修复以下 SQL 语句：\n```sql\n{sql_query}\n```"

        llm = get_llm(temperature=0.2)
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
            logger.info(f"LLM 验证修复结果 - is_valid: {result.get('is_valid')}, "
                       f"llm_validation_passed: {result.get('llm_validation_passed')}, "
                       f"errors: {result.get('errors')}, "
                       f"warnings: {result.get('warnings')}, "
                       f"fixed_sql: {result.get('fixed_sql') != result.get('original_sql')}")
        except json.JSONDecodeError:
            result["errors"].append("LLM 返回格式错误")
            logger.error(f"LLM 验证修复结果解析失败，返回内容: {response_content}")

    except Exception as e:
        result["errors"].append(f"LLM 验证修复过程异常: {str(e)}")
        logger.error(f"LLM 验证修复过程异常: {e}", exc_info=True)

    return result





def syntax_validator(state: AgentState) -> AgentState:
    """
    语法验证智能体：优化后的验证流程
    1. 先使用数据库验证
    2. 验证通过直接结束
    3. 验证失败则LLM修复，再数据库验证

    Args:
        state: 智能体状态

    Returns:
        更新后的状态
    """
    logger.info("语法验证智能体开始工作（优化流程）")

    fix_attempts = state.get("fix_attempts", 0)
    max_fix_attempts = 2

    try:
        generated_sql = state.get("generated_sql", "")
        datasource_id = state.get("datasource_id")
        db_type = state.get("db_type", "mysql")

        logger.info(f"开始验证 SQL: {generated_sql}")
        logger.info(f"数据源ID: {datasource_id}")
        logger.info(f"数据库类型: {db_type}")
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

        schema_text = state.get("db_info", "")

        if not schema_text and datasource_id:
            try:
                datasource_schema = get_datasource_schema(datasource_id)
                schema_text = format_schema_for_prompt(datasource_schema)
                logger.info(f"从数据库获取到数据源表结构并格式化")
            except ImportError as e:
                logger.warning(f"无法导入 get_datasource_schema: {e}")
                schema_text = ""
        elif schema_text:
            logger.info(f"使用 state 中的数据源表结构（已格式化）")

        current_sql = generated_sql
        datasource_config = None
        all_errors = []
        all_warnings = []
        validation_passed = False
        explain_result = None
        llm_validation_passed = False
        llm_feedback = ""

        for attempt in range(fix_attempts, max_fix_attempts + 1):
            logger.info(f"验证修复尝试 {attempt + 1}/{max_fix_attempts + 1}")

            if datasource_id:
                try:
                    if datasource_config is None:
                        datasource_config = state.get("datasource_config")
                        
                        if datasource_config is None:
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
                            warning_msg = f"数据源配置不完整，缺少字段: {missing_fields}，跳过数据库验证"
                            all_warnings.append(warning_msg)
                            logger.warning(warning_msg)
                        else:
                            temp_state = state.copy()
                            temp_state["generated_sql"] = current_sql

                            db_result = validate_sql_with_database(temp_state, datasource_config)
                            db_errors = db_result.get("errors", [])
                            db_warnings = db_result.get("warnings", [])
                            validation_passed = db_result.get("validation_passed", False)
                            explain_result = db_result.get("explain_result")
                            logger.info(f"数据库验证结果: {'通过' if validation_passed else '失败'}")

                            if validation_passed:
                                all_warnings.extend(db_warnings)
                                logger.info("数据库验证通过，直接结束验证流程 ✅")
                                break
                            else:
                                all_errors = db_errors
                                logger.error(f"数据库验证错误: {db_errors}")
                                state["db_errors"] = db_errors
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

            if attempt < max_fix_attempts:
                logger.info("数据库验证失败，开始 LLM 修复")
                
                try:
                    current_state = state.copy()
                    current_state["generated_sql"] = current_sql

                    llm_result = validate_and_fix_with_llm(current_state, schema_text, db_type)
                    llm_validation_passed = llm_result.get("llm_validation_passed", False)
                    llm_feedback = llm_result.get("llm_feedback", "")
                    fixed_sql = llm_result.get("fixed_sql", current_sql)
                    
                    logger.info(f"LLM 验证修复结果: {'通过' if llm_validation_passed else '失败'}")
                    if fixed_sql != current_sql:
                        logger.info(f"SQL 已被修复: {fixed_sql}")
                        current_sql = fixed_sql
                        state["was_fixed"] = True
                        state["fix_attempts"] = attempt + 1
                except Exception as e:
                    error_msg = f"LLM 验证修复异常: {str(e)}"
                    all_errors.append(error_msg)
                    logger.error(error_msg, exc_info=True)
            else:
                logger.info("已达到最大修复次数")
                break

        is_valid = validation_passed or len(all_errors) == 0

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
        state["generated_sql"] = current_sql

        if is_valid:
            logger.info(f"SQL 语法验证通过 (修复尝试: {state.get('fix_attempts', 0)}次)")
            state["validated_sql"] = current_sql
            logger.info(f"已保存验证成功的SQL: {current_sql}")
            if all_warnings:
                logger.warning(f"验证警告: {all_warnings}")
        else:
            logger.error(f"SQL 语法验证失败，已尝试修复 {max_fix_attempts} 次: {all_errors}")

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
