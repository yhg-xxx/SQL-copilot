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


def extract_index_info_from_db_info(db_info):
    """从 db_info 中提取索引信息"""
    indexes = []
    
    if not db_info:
        return indexes
    
    for table_name, table_info in db_info.items():
        fields = table_info.get('fields', [])
        for field in fields:
            if field.get('is_indexed'):
                indexes.append({
                    'table_name': table_name,
                    'column_name': field.get('name'),
                    'index_name': field.get('index_name', 'unknown'),
                    'index_type': field.get('index_type', 'INDEX'),
                    'non_unique': 1 if field.get('index_type') != 'PRIMARY' else 0
                })
    
    return indexes


def analyze_index_usage(sql_structure, indexes):
    """分析索引使用情况"""
    used_indexes = []
    missing_indexes = []
    
    # 检查WHERE条件中的索引使用
    for condition in sql_structure['where_conditions']:
        for table in sql_structure['tables']:
            table_indexes = [idx for idx in indexes if idx['table_name'] == table]
            table_columns = [idx['column_name'] for idx in table_indexes]
            
            for column in table_columns:
                if column in condition:
                    used_indexes.append({'table': table, 'column': column, 'index_name': [idx['index_name'] for idx in table_indexes if idx['column_name'] == column][0]})
    
    # 检查ORDER BY中的索引使用
    for order in sql_structure['order_by']:
        for table in sql_structure['tables']:
            table_indexes = [idx for idx in indexes if idx['table_name'] == table]
            for column in [idx['column_name'] for idx in table_indexes]:
                if column in order:
                    used_indexes.append({'table': table, 'column': column, 'index_name': [idx['index_name'] for idx in table_indexes if idx['column_name'] == column][0]})
    
    return {
        'used_indexes': used_indexes,
        'missing_indexes': missing_indexes
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


def generate_natural_language_comment(sql, sql_structure, user_query):
    """生成自然语言注释"""
    comments = ["-- SQL 语句功能说明："]

    # 分析数据来源
    if sql_structure['tables']:
        tables_str = ', '.join(sql_structure['tables'])
        comments.append(f"-- 数据来源：{tables_str} 表")
    else:
        comments.append("-- 数据来源：未知")
    
    # 分析数据类型
    if 'COUNT(' in sql.upper():
        comments.append("-- 数据类型：统计数据")
    elif 'SELECT *' in sql.upper():
        comments.append("-- 数据类型：完整数据")
    elif 'SELECT ' in sql.upper():
        comments.append("-- 数据类型：部分字段数据")
    else:
        comments.append("-- 数据类型：未知")
    
    # 分析查询目的
    if user_query:
        # 确保用户查询不包含换行符
        user_query_clean = user_query.replace('\n', ' ').strip()
        comments.append(f"-- 查询目的：{user_query_clean}")
    else:
        comments.append(f"-- 查询目的：{sql_structure['tables'][0] if sql_structure['tables'] else '数据'} 相关信息")
    
    # 其他条件
    if sql_structure['group_by']:
        # 清理GROUP BY条件，确保不包含换行符
        group_by = sql_structure['group_by'][0].replace('\n', ' ').strip()
        # 只保留GROUP BY关键字后的内容
        if 'GROUP BY' in group_by.upper():
            group_by = group_by.split('GROUP BY', 1)[1].strip()
        comments.append(f"-- 分组方式：{group_by}")
    
    natural_language_comment = '\n'.join(comments) + '\n'
    return natural_language_comment


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
        
        # 2. 从 db_info 中提取索引信息
        indexes = extract_index_info_from_db_info(db_info)
        logger.info(f"从 db_info 中提取的索引信息: {indexes}")
        
        # 3. 分析索引使用情况
        index_usage = analyze_index_usage(sql_structure, indexes)
        logger.info(f"索引使用分析结果: {index_usage}")
        
        # 4. 使用大模型生成优化建议
        llm_result = generate_optimization_suggestions(generated_sql, db_info, user_query)
        logger.info(f"LLM 优化分析结果: {llm_result}")
        
        # 5. 生成自然语言注释
        natural_language_comment = generate_natural_language_comment(generated_sql, sql_structure, user_query)
        
        # 6. 生成最终优化后的SQL
        if llm_result.get("optimized") and llm_result.get("optimized_sql"):
            optimized_sql = llm_result.get("optimized_sql")
            # 添加注释
            optimized_sql = f"{optimized_sql}\n{natural_language_comment}"
        else:
            # 如果LLM没有返回优化后的SQL，使用原始SQL并添加注释
            optimized_sql = f"{generated_sql}\n{natural_language_comment}"
        
        # 7. 构建优化结果
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
