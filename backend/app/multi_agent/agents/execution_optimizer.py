import logging
import sqlparse
import re
import json

from langchain_core.messages import SystemMessage, HumanMessage

from app.multi_agent.state.agent_state import AgentState, OptimizationResult
from app.utils.llm_util import get_llm

logger = logging.getLogger(__name__)


def analyze_sql_structure(sql):
    """分析SQL语句结构"""
    parsed = sqlparse.parse(sql)[0]
    tables = []
    where_conditions = []
    join_conditions = []
    group_by = []
    order_by = []
    
    # 简单解析，实际项目中可能需要更复杂的解析
    for token in parsed.tokens:
        if isinstance(token, sqlparse.sql.IdentifierList):
            for identifier in token.get_identifiers():
                if '.' in str(identifier):
                    tables.append(str(identifier).split('.')[-1].strip('`'))
                else:
                    tables.append(str(identifier).strip('`'))
        elif isinstance(token, sqlparse.sql.Where):
            where_conditions.append(str(token))
        # 检查是否包含 JOIN 关键字
        elif 'JOIN' in str(token).upper():
            join_conditions.append(str(token))
        # 检查是否包含 GROUP BY 关键字
        elif 'GROUP BY' in str(token).upper():
            group_by.append(str(token))
        # 检查是否包含 ORDER BY 关键字
        elif 'ORDER BY' in str(token).upper():
            order_by.append(str(token))
    
    # 使用正则表达式从 SQL 语句中提取表名
    from_match = re.search(r'FROM\s+([\w`]+)', sql, re.IGNORECASE)
    if from_match:
        table_name = from_match.group(1).strip('`')
        if table_name and table_name not in tables:
            tables.append(table_name)
    
    # 检查 JOIN 语句中的表名
    join_matches = re.findall(r'\b(?:LEFT|RIGHT|INNER|OUTER|CROSS)\s+JOIN\s+([\w`]+)', sql, re.IGNORECASE)
    for table_name in join_matches:
        table_name = table_name.strip('`')
        if table_name and table_name not in tables:
            tables.append(table_name)
    
    return {
        'tables': tables,
        'where_conditions': where_conditions,
        'join_conditions': join_conditions,
        'group_by': group_by,
        'order_by': order_by
    }


def generate_optimization_suggestions(sql, db_info, user_query):
    """使用大模型生成SQL优化建议"""
    try:
        # 准备表结构信息
        schema_text = ""
        if db_info:
            schema_text = "数据库表结构信息:\n"
            for table_name, table_info in db_info.items():
                schema_text += f"\n表: {table_name}"
                if table_info.get('comment'):
                    schema_text += f" ({table_info['comment']})"
                schema_text += "\n字段:"
                for field in table_info.get('fields', []):
                    field_desc = f"  - {field['name']} ({field['type']})"
                    if field.get('comment'):
                        field_desc += f": {field['comment']}"
                    if field.get('is_indexed'):
                        index_type = field.get('index_type') or 'INDEX'
                        index_name = field.get('index_name') or 'unknown'
                        field_desc += f" [{index_type} 索引: {index_name}]"
                    schema_text += f"\n{field_desc}"
        
        system_prompt = f"""你是一个专业的 SQL 性能优化专家。请根据以下信息对给定的 SQL 语句进行性能分析和优化建议：

{schema_text}

用户原始查询需求：{user_query}

请分析以下 SQL 语句的性能问题，并提供具体的优化建议，包括：
1. 索引使用情况分析
2. 查询结构优化建议
3. 可能的性能瓶颈
4. 优化后的 SQL 语句

重要约束：
- 只能使用上述表结构信息中已有的索引，不要建议或使用不存在的索引
- 不要在优化后的 SQL 语句中使用 FORCE INDEX 或类似的索引强制提示
- 只基于现有的表结构和索引信息进行优化
- 优化后的 SQL 语句必须在语法上正确，并且可以直接执行

请只返回 JSON 格式的结果，不要包含其他文字。

JSON 格式：
{{
  "optimized": true/false,
  "optimized_sql": "优化后的 SQL 语句",
  "suggestions": ["建议1", "建议2"],
  "execution_notes": "执行注释"
}}
"""
        
        user_prompt = f"请分析并优化以下 SQL 语句：\n```sql\n{sql}\n```"
        
        # 调用 LLM
        llm = get_llm(temperature=0.1)
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
        
        # 解析 JSON
        try:
            result = json.loads(response_content)
            return result
        except json.JSONDecodeError:
            logger.error(f"LLM 返回格式错误: {response_content}")
            return {
                "optimized": False,
                "optimized_sql": sql,
                "suggestions": ["LLM 分析失败，使用默认优化"],
                "execution_notes": ""
            }
            
    except Exception as e:
        logger.error(f"生成优化建议时发生错误: {e}", exc_info=True)
        return {
            "optimized": False,
            "optimized_sql": sql,
            "suggestions": [f"优化分析失败: {str(e)}"],
            "execution_notes": ""
        }


def generate_sql_comment(sql, db_info, user_query):
    """使用大模型生成SQL语句功能说明"""
    try:
        logger.info("开始生成 SQL 语句功能说明")
        logger.info(f"分析的 SQL 语句: {sql}")
        logger.info(f"用户原始查询: {user_query}")
        
        # 准备表结构信息
        schema_text = ""
        if db_info:
            schema_text = "数据库表结构信息:\n"
            table_count = len(db_info)
            logger.info(f"数据库表结构信息包含 {table_count} 个表")
            
            for table_name, table_info in db_info.items():
                schema_text += f"\n表: {table_name}"
                if table_info.get('comment'):
                    schema_text += f" ({table_info['comment']})"
                schema_text += "\n字段:"
                field_count = len(table_info.get('fields', []))
                logger.info(f"表 {table_name} 包含 {field_count} 个字段")
                
                for field in table_info.get('fields', []):
                    field_desc = f"  - {field['name']} ({field['type']})"
                    if field.get('comment'):
                        field_desc += f": {field['comment']}"
                    schema_text += f"\n{field_desc}"
        else:
            logger.info("未提供数据库表结构信息")
        
        system_prompt = f"""你是一个专业的 SQL 语句分析专家。请根据以下信息对给定的 SQL 语句生成详细的功能说明：

{schema_text}

用户原始查询需求：{user_query}

请分析以下 SQL 语句的功能，并生成详细的功能说明，包括：
1. 数据来源：列出 SQL 语句中涉及的所有表
2. 数据类型：描述查询结果的类型（如统计数据、详细记录等）
3. 查询目的：用自然语言清晰解释 SQL 语句的具体功能，描述它实现了什么业务逻辑
4. 核心逻辑：解释 SQL 语句的主要实现方法和执行流程

重要要求：
- 查询目的必须是对 SQL 语句功能的客观解释，绝对不要直接重复用户的原始问题
- 请基于 SQL 语句的实际内容进行分析，而不是基于用户的问题描述
- 用简洁明了的自然语言表达，避免技术术语过多

请只返回注释格式的结果，不要包含其他文字。

示例：
用户问题：我想知道每个用户的总购买金额
SQL：SELECT user_id, SUM(amount) FROM orders GROUP BY user_id;

正确的功能说明：
-- SQL 语句功能说明：
-- 数据来源：orders 表
-- 数据类型：统计数据
-- 查询目的：计算每个用户的总购买金额
-- 核心逻辑：根据用户ID分组，对每个用户的购买金额进行求和

请按照上述示例格式生成功能说明。
"""
        
        user_prompt = f"请分析以下 SQL 语句并生成功能说明：\n```sql\n{sql}\n```"
        
        # 调用 LLM
        logger.info("调用大模型生成 SQL 语句功能说明")
        llm = get_llm(temperature=0.1)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        
        response = llm.invoke(messages)
        response_content = response.content.strip()
        logger.info(f"大模型返回的原始响应: {response_content[:200]}...")
        
        # 清理响应
        if "```sql" in response_content:
            response_content = response_content.split("```sql")[1]
            logger.info("清理 SQL 代码块标记")
        if "```" in response_content:
            response_content = response_content.split("```")[0]
            logger.info("清理代码块标记")
        response_content = response_content.strip()
        logger.info(f"清理后的响应: {response_content[:200]}...")
        
        # 确保响应以注释格式开头
        if not response_content.startswith("--"):
            # 如果LLM没有返回注释格式，使用默认格式
            logger.warning("LLM 返回的响应不是注释格式，使用默认格式")
            default_comment = "-- SQL 语句功能说明：\n"
            default_comment += "-- 数据来源：未知\n"
            default_comment += "-- 数据类型：未知\n"
            default_comment += "-- 查询目的：未知\n"
            default_comment += "-- 核心逻辑：未知\n"
            logger.info("使用默认功能说明")
            return default_comment
        
        # 确保注释以换行符结尾
        if not response_content.endswith('\n'):
            response_content += '\n'
        
        logger.info("SQL 语句功能说明生成完成")
        logger.info(f"生成的功能说明: {response_content[:200]}...")
        return response_content
        
    except Exception as e:
        logger.error(f"生成 SQL 语句功能说明时发生错误: {e}", exc_info=True)
        # 出错时返回默认注释
        default_comment = "-- SQL 语句功能说明：\n"
        default_comment += "-- 数据来源：未知\n"
        default_comment += "-- 数据类型：未知\n"
        default_comment += "-- 查询目的：未知\n"
        default_comment += "-- 核心逻辑：未知\n"
        logger.info("发生错误，使用默认功能说明")
        return default_comment


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
        
        # 1. 解析SQL语句结构
        sql_structure = analyze_sql_structure(generated_sql)
        logger.info(f"SQL结构分析结果: {sql_structure}")

        # 2. 使用大模型生成优化建议
        llm_result = generate_optimization_suggestions(generated_sql, db_info, user_query)
        logger.info(f"LLM 优化分析结果: {llm_result}")
        
        # 3. 生成SQL语句功能说明（使用智能体）
        natural_language_comment = generate_sql_comment(generated_sql, db_info, user_query)
        
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
