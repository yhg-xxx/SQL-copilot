import logging
import sqlparse
from typing import Dict, List, Any, Optional

from app.multi_agent.state.agent_state import AgentState, OptimizationResult

logger = logging.getLogger(__name__)


def get_table_indexes(cursor, database, table_name):
    """获取表的索引信息"""
    cursor.execute(f"SHOW INDEX FROM `{database}`.`{table_name}`")
    indexes = cursor.fetchall()
    
    index_list = []
    for index in indexes:
        index_list.append({
            'index_name': index[2],
            'column_name': index[4],
            'non_unique': index[1],
            'seq_in_index': index[3],
            'index_type': index[10]
        })
    
    return index_list


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
    import re
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


def analyze_index_usage(sql_structure, indexes):
    """分析索引使用情况"""
    used_indexes = []
    missing_indexes = []
    
    # 检查WHERE条件中的索引使用
    for condition in sql_structure['where_conditions']:
        # 简单实现，实际项目中需要更复杂的分析
        for table in sql_structure['tables']:
            table_indexes = [idx for idx in indexes if idx['table_name'] == table]
            table_columns = [idx['column_name'] for idx in table_indexes]
            
            for column in table_columns:
                if column in condition:
                    used_indexes.append({'table': table, 'column': column, 'index_name': [idx['index_name'] for idx in table_indexes if idx['column_name'] == column][0]})
                else:
                    # 检查是否有未使用的索引字段
                    if column in condition:
                        used_indexes.append({'table': table, 'column': column, 'index_name': [idx['index_name'] for idx in table_indexes if idx['column_name'] == column][0]})
    
    return {
        'used_indexes': used_indexes,
        'missing_indexes': missing_indexes
    }


def generate_natural_language_comment(sql_structure, index_usage, performance_analysis):
    """生成自然语言注释"""
    comments = []
    comments.append("/*")
    comments.append("===================================================================")
    comments.append("                        SQL 查询分析报告                         ")
    comments.append("===================================================================")
    
    # 分析 SQL 功能
    comments.append("\n【SQL 查询功能说明】")
    if sql_structure['tables']:
        tables_str = ', '.join(sql_structure['tables'])
        comments.append(f"- 查询涉及的表：{tables_str}")
    else:
        comments.append("- 查询涉及的表：无")
    
    if sql_structure['where_conditions']:
        comments.append("- 过滤条件：存在 WHERE 子句，对数据进行筛选")
    else:
        comments.append("- 过滤条件：无")
    
    if sql_structure['join_conditions']:
        comments.append("- 连接操作：存在 JOIN 子句，关联多个表的数据")
    else:
        comments.append("- 连接操作：无")
    
    if sql_structure['group_by']:
        comments.append("- 分组操作：存在 GROUP BY 子句，对数据进行分组统计")
    else:
        comments.append("- 分组操作：无")
    
    if sql_structure['order_by']:
        comments.append("- 排序操作：存在 ORDER BY 子句，对结果进行排序")
    else:
        comments.append("- 排序操作：无")
    
    # 索引使用情况
    comments.append("\n【索引使用情况】")
    if index_usage['used_indexes']:
        index_notes = []
        for idx in index_usage['used_indexes']:
            index_notes.append(f"{idx['table']}表的{idx['index_name']}索引")
        comments.append(f"- 使用了以下索引：{', '.join(index_notes)}")
    else:
        comments.append("- 未使用任何索引，可能影响查询性能")
    
    # 性能分析
    comments.append("\n【性能分析】")
    if performance_analysis:
        comments.append(f"- 性能瓶颈：{performance_analysis.get('bottleneck', '无明显瓶颈')}")
        comments.append(f"- 预计执行时间：{performance_analysis.get('estimated_time', '< 0.1秒')}")
    else:
        comments.append("- 性能瓶颈：无明显瓶颈")
        comments.append("- 预计执行时间：< 0.1秒")
    
    # 优化建议
    comments.append("\n【优化建议】")
    if index_usage['missing_indexes']:
        suggestions = []
        for idx in index_usage['missing_indexes']:
            suggestions.append(f"为{idx['table']}表的{idx['column']}字段添加索引")
        comments.append(f"- {'; '.join(suggestions)}")
    else:
        comments.append("- 暂无优化建议")
    
    comments.append("\n===================================================================")
    comments.append("*/")
    
    return '\n'.join(comments)


def generate_execution_notes(sql_structure, index_usage, performance_analysis):
    """生成执行注释"""
    notes = []
    notes.append("-- ===================================================================")
    notes.append("--                        执行优化注释                              ")
    notes.append("-- ===================================================================")
    
    # 索引使用情况
    notes.append("-- ")
    notes.append("-- 【索引使用情况】")
    if index_usage['used_indexes']:
        index_notes = []
        for idx in index_usage['used_indexes']:
            index_notes.append(f"{idx['table']}表的{idx['index_name']}索引")
        notes.append(f"-- 使用了以下索引：{', '.join(index_notes)}")
    else:
        notes.append("-- 未使用任何索引，可能影响查询性能")
    
    # 性能瓶颈分析
    notes.append("-- ")
    notes.append("-- 【性能分析】")
    if performance_analysis:
        notes.append(f"-- 性能瓶颈：{performance_analysis.get('bottleneck', '无明显瓶颈')}")
        notes.append(f"-- 预计执行时间：{performance_analysis.get('estimated_time', '< 0.1秒')}")
    else:
        notes.append("-- 性能瓶颈：无明显瓶颈")
        notes.append("-- 预计执行时间：< 0.1秒")
    
    # 优化建议
    notes.append("-- ")
    notes.append("-- 【优化建议】")
    if index_usage['missing_indexes']:
        suggestions = []
        for idx in index_usage['missing_indexes']:
            suggestions.append(f"为{idx['table']}表的{idx['column']}字段添加索引")
        notes.append(f"-- {'; '.join(suggestions)}")
    else:
        notes.append("-- 暂无优化建议")
    
    notes.append("-- ")
    notes.append("-- ===================================================================")
    
    return '\n'.join(notes)


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
        
        # 2. 分析索引使用情况（模拟，实际项目中需要从数据源获取索引信息）
        # 这里使用模拟数据，实际项目中需要从数据库获取真实的索引信息
        mock_indexes = []
        for table in sql_structure['tables']:
            mock_indexes.append({'table_name': table, 'column_name': 'id', 'index_name': 'PRIMARY', 'non_unique': 0, 'seq_in_index': 1, 'index_type': 'BTREE'})
        
        index_usage = analyze_index_usage(sql_structure, mock_indexes)
        logger.info(f"索引使用分析结果: {index_usage}")
        
        # 3. 执行计划分析（模拟）
        performance_analysis = {
            'bottleneck': '无明显瓶颈',
            'estimated_time': '< 0.1秒'
        }
        
        # 5. 生成自然语言注释（只保留对 SQL 语言的解释，只显示有数据的说明）
        comments = []
        comments.append("-- SQL 语句功能说明：")
        
        # 分析数据来源
        if sql_structure['tables']:
            tables_str = ', '.join(sql_structure['tables'])
            comments.append(f"-- 数据来源：{tables_str} 表")
        else:
            comments.append("-- 数据来源：未知")
        
        # 分析数据类型
        if 'COUNT(' in generated_sql.upper():
            comments.append("-- 数据类型：统计数据")
        elif 'SELECT *' in generated_sql.upper():
            comments.append("-- 数据类型：完整数据")
        elif 'SELECT ' in generated_sql.upper():
            comments.append("-- 数据类型：部分字段数据")
        else:
            comments.append("-- 数据类型：未知")
        
        # 分析查询目的
        comments.append(f"-- 查询目的：{sql_structure['tables'][0] if sql_structure['tables'] else '数据'} 相关信息")
        
        # 其他条件
        if sql_structure['where_conditions']:
            comments.append(f"-- 查询条件：{sql_structure['where_conditions'][0]}")
        
        if sql_structure['order_by']:
            comments.append(f"-- 排序方式：{sql_structure['order_by'][0]}")
        
        if sql_structure['group_by']:
            comments.append(f"-- 分组方式：{sql_structure['group_by'][0]}")
        
        natural_language_comment = '\n'.join(comments) + '\n'
        
        # 6. 生成优化后的SQL（当前版本不做实际优化，仅添加注释）
        optimized_sql = f"{generated_sql}\n{natural_language_comment}"
        
        # 6. 构建优化结果
        optimization_result = OptimizationResult(
            optimized=True,
            optimized_sql=optimized_sql,
            suggestions=["已添加 SQL 语句功能说明"]
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
