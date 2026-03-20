import logging
import json
import sqlparse
from langchain_core.messages import SystemMessage, HumanMessage
from app.multi_agent.state.agent_state import AgentState, OptimizationResult

from app.utils.llm_util import get_llm
from app.multi_agent.prompts.database_optimization_prompts import get_optimization_prompt_by_db_type

logger = logging.getLogger(__name__)


def generate_optimization_suggestions(sql, schema_text, user_query, db_type, execution_plan=None):
    """使用大模型生成SQL优化建议"""
    try:
        logger.info("开始生成 SQL 优化建议和功能说明")
        logger.info(f"分析的 SQL 语句: {sql}")
        logger.info(f"用户原始查询: {user_query}")
        logger.info(f"数据库类型: {db_type}")

        # 准备表结构信息
        schema_text = schema_text or ""

        # 根据数据库类型获取特定的优化提示词
        system_prompt = get_optimization_prompt_by_db_type(db_type, schema_text, user_query, execution_plan)
        
        user_prompt = f"请分析并优化以下 SQL 语句，并生成功能说明：\n```sql\n{sql}\n```"
        if execution_plan:
            user_prompt += f"\n\n以下是该 SQL 的数据库执行计划（仅供参考）：\n{execution_plan}"
        
        # 调用 LLM
        logger.info("调用大模型生成 SQL 优化建议和功能说明")
        llm = get_llm(temperature=0.1)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        
        response = llm.invoke(messages)
        response_content = response.content.strip()
        logger.info(f"大模型返回的原始响应: {response_content[:200]}...")

        # 清理响应
        if "```json" in response_content:
            response_content = response_content.split("```json")[1]
            logger.info("清理 JSON 代码块标记")
        if "```" in response_content:
            response_content = response_content.split("```")[0]
            logger.info("清理代码块标记")
        response_content = response_content.strip()
        logger.info(f"清理后的响应: {response_content[:200]}...")

        # 解析 JSON
        try:
            result = json.loads(response_content)
            logger.info("成功解析 LLM 返回的 JSON")
            return result
        except json.JSONDecodeError:
            logger.error(f"LLM 返回格式错误: {response_content}")
            # 返回默认结果
            return {
                "optimized": False,
                "optimized_sql": sql,
                "suggestions": ["LLM 分析失败，使用默认优化"],
                "execution_notes": "",
                "functional_description": {
                    "data_source": "未知",
                    "core_logic": "未知"
                }
            }
            
    except Exception as e:
        logger.error(f"生成优化建议和功能说明时发生错误: {e}", exc_info=True)
        # 返回默认结果
        return {
            "optimized": False,
            "optimized_sql": sql,
            "suggestions": [f"分析失败: {str(e)}"],
            "execution_notes": "",
            "functional_description": {
                "data_source": "未知",
                "core_logic": "未知"
            }
        }

def generate_comment_from_functional_description(func_desc):
    """根据功能说明生成注释格式"""
    comment = "-- SQL 语句功能说明：\n"
    comment += f"-- 数据来源：{func_desc.get('data_source', '未知')}\n"
    comment += f"-- 核心逻辑：{func_desc.get('core_logic', '未知')}\n"
    comment += ""  # 添加一个空行，使注释与 SQL 主体分离更清晰
    return comment


def execution_optimizer(state: AgentState) -> AgentState:
    """
    执行优化智能体：负责优化查询性能并添加执行注释
    
    Args:
        state: 智能体状态
        
    Returns:
        更新后的状态
    """
    logger.info("执行优化智能体开始工作")
    
    try:
        generated_sql = state.get("generated_sql", "")
        validation_result = state.get("validation_result")
        user_query = state.get("user_query", "")
        schema_text = state.get("db_info", "")
        
        if not generated_sql or generated_sql == "No SQL query generated":
            optimization_result = OptimizationResult(
                optimized=False,
                suggestions=["没有可优化的 SQL"]
            )
            state["optimization_result"] = optimization_result
            state["final_sql"] = generated_sql
            return state
        
        # 检查验证结果
        if validation_result and not validation_result.valid:
            optimization_result = OptimizationResult(
                optimized=False,
                suggestions=["SQL 未通过验证，无法进行优化"]
            )
            state["optimization_result"] = optimization_result
            state["final_sql"] = generated_sql
            return state


        # 2. 获取数据库类型和执行计划
        db_type = state.get("db_type", "mysql")
        execution_plan = state.get("execution_plan")
        
        # 3. 使用大模型同时生成优化建议和功能说明
        llm_result = generate_optimization_suggestions(generated_sql, schema_text, user_query, db_type, execution_plan)
        logger.info(f"LLM 分析结果: {llm_result}")
        
        # 4. 提取功能说明并生成注释
        functional_description = llm_result.get("functional_description", {})
        natural_language_comment = generate_comment_from_functional_description(functional_description)
        logger.info(f"生成的功能说明注释: {natural_language_comment[:200]}...")
        
        # 5. 生成最终优化后的 SQL
        if llm_result.get("optimized") and llm_result.get("optimized_sql"):
            optimized_sql = llm_result.get("optimized_sql")
            # 使用 sqlparse 格式化 SQL
            optimized_sql = sqlparse.format(optimized_sql, reindent=True, keyword_case='upper')
            # 添加注释
            optimized_sql = f"{optimized_sql}\n{natural_language_comment}"
        else:
            # 如果 LLM 没有返回优化后的 SQL，使用原始 SQL 并添加注释
            # 先格式化原始 SQL
            formatted_sql = sqlparse.format(generated_sql, reindent=True, keyword_case='upper')
            optimized_sql = f"{formatted_sql}\n{natural_language_comment}"
        
        # 6. 构建优化结果
        suggestions = llm_result.get("suggestions", [])
        if not suggestions:
            suggestions = ["已添加 SQL 语句功能说明"]
        
        optimization_result = OptimizationResult(
            optimized=True,
            optimized_sql=optimized_sql,
            suggestions=suggestions
        )
        
        state["optimization_result"] = optimization_result
        state["optimized_sql"] = optimized_sql
        state["final_sql"] = optimized_sql
        logger.info("SQL 执行优化完成")
        
    except Exception as e:
        logger.error(f"执行优化过程中发生错误: {e}", exc_info=True)
        optimization_result = OptimizationResult(
            optimized=False,
            suggestions=[f"优化过程出错: {str(e)}"]
        )
        state["optimization_result"] = optimization_result
        state["final_sql"] = state.get("generated_sql", "")
        state["error_message"] = f"执行优化失败: {str(e)}"
    
    return state
