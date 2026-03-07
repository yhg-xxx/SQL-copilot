import logging
import json
from langchain_core.messages import SystemMessage, HumanMessage
from app.multi_agent.state.agent_state import AgentState, OptimizationResult
from app.multi_agent.agents.schema_utils import format_schema_for_prompt
from app.utils.llm_util import get_llm

logger = logging.getLogger(__name__)


def generate_optimization_suggestions(sql, db_info, user_query):
    """使用大模型生成SQL优化建议"""
    try:
        logger.info("开始生成 SQL 优化建议和功能说明")
        logger.info(f"分析的 SQL 语句: {sql}")
        logger.info(f"用户原始查询: {user_query}")

        # 准备表结构信息
        schema_text = format_schema_for_prompt(db_info) if db_info else ""

        system_prompt = f"""你是一个专业的 SQL 性能优化专家。请根据以下信息对给定的 SQL 语句进行性能分析和优化建议：

{schema_text}

用户原始查询需求：{user_query}

请分析以下 SQL 语句的性能问题，并提供具体的优化建议，包括：
1. 索引使用情况分析
2. 查询结构优化建议
3. 可能的性能瓶颈
4. 优化后的 SQL 语句

同时，请分析 SQL 语句的功能，并生成详细的功能说明，包括：
1. 数据来源：列出 SQL 语句中涉及的所有表
2. 数据类型：描述查询结果的类型（如统计数据、详细记录等）
3. 查询目的：用自然语言清晰解释 SQL 语句的具体功能，描述它实现了什么业务逻辑
4. 核心逻辑：解释 SQL 语句的主要实现方法和执行流程

重要约束：
- 只能使用上述表结构信息中已有的索引，不要建议或使用不存在的索引
- 不要在优化后的 SQL 语句中使用 FORCE INDEX 或类似的索引强制提示
- 只基于现有的表结构和索引信息进行优化
- 优化后的 SQL 语句必须在语法上正确，并且可以直接执行
- 查询目的必须是对 SQL 语句功能的客观解释，绝对不要直接重复用户的原始问题
- 请基于 SQL 语句的实际内容进行分析，而不是基于用户的问题描述
- 用简洁明了的自然语言表达，避免技术术语过多

请只返回 JSON 格式的结果，不要包含其他文字。

JSON 格式：
{{
  "optimized": true/false,
  "optimized_sql": "优化后的 SQL 语句",
  "suggestions": ["建议1", "建议2"],
  "execution_notes": "执行注释",
  "functional_description": {{
    "data_source": "涉及的表",
    "data_type": "数据类型",
    "query_purpose": "查询目的",
    "core_logic": "核心逻辑"
  }}
}}
"""
        
        user_prompt = f"请分析并优化以下 SQL 语句，并生成功能说明：\n```sql\n{sql}\n```"
        
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
                    "data_type": "未知",
                    "query_purpose": "未知",
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
                "data_type": "未知",
                "query_purpose": "未知",
                "core_logic": "未知"
            }
        }

def generate_comment_from_functional_description(func_desc):
    """根据功能说明生成注释格式"""
    comment = "-- SQL 语句功能说明：\n"
    comment += f"-- 数据来源：{func_desc.get('data_source', '未知')}\n"
    comment += f"-- 数据类型：{func_desc.get('data_type', '未知')}\n"
    comment += f"-- 查询目的：{func_desc.get('query_purpose', '未知')}\n"
    comment += f"-- 核心逻辑：{func_desc.get('core_logic', '未知')}\n"
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
        db_info = state.get("db_info", {})
        
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


        # 2. 使用大模型同时生成优化建议和功能说明
        llm_result = generate_optimization_suggestions(generated_sql, db_info, user_query)
        logger.info(f"LLM 分析结果: {llm_result}")
        
        # 3. 提取功能说明并生成注释
        functional_description = llm_result.get("functional_description", {})
        natural_language_comment = generate_comment_from_functional_description(functional_description)
        logger.info(f"生成的功能说明注释: {natural_language_comment[:200]}...")
        
        # 4. 生成最终优化后的SQL
        if llm_result.get("optimized") and llm_result.get("optimized_sql"):
            optimized_sql = llm_result.get("optimized_sql")
            # 添加注释
            optimized_sql = f"{optimized_sql}\n{natural_language_comment}"
        else:
            # 如果LLM没有返回优化后的SQL，使用原始SQL并添加注释
            optimized_sql = f"{generated_sql}\n{natural_language_comment}"
        
        # 5. 构建优化结果
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
