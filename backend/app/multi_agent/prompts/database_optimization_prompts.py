import logging

logger = logging.getLogger(__name__)


def get_mysql_optimization_prompt(schema_text, user_query, execution_plan=None):
    """
    获取 MySQL 特定的 SQL 优化提示词

    Args:
        schema_text: 数据库表结构信息
        user_query: 用户原始查询需求
        execution_plan: 数据库执行计划（可选）

    Returns:
        MySQL 特定的优化提示词
    """
    execution_plan_section = ""
    if execution_plan:
        execution_plan_section = f"""
数据库执行计划：
{execution_plan}

"""
    return f"""你是一个专业的 MySQL SQL 性能优化专家。请根据以下信息对给定的 SQL 语句进行性能分析和优化建议：

{schema_text}

用户原始查询需求：{user_query}

{execution_plan_section}
请分析以下 SQL 语句的性能问题，并提供具体的优化建议，包括：
1. 索引使用情况分析
2. 查询结构优化建议
3. 可能的性能瓶颈
4. 优化后的 SQL 语句

同时，请分析 SQL 语句的功能，并生成详细的功能说明，包括：
1. 数据来源：列出 SQL 语句中涉及的所有表
2. 核心逻辑：解释 SQL 语句的主要实现方法和执行流程

重要约束：
- 只能使用上述表结构信息中已有的索引，不要建议或使用不存在的索引
- 不要在优化后的 SQL 语句中使用 FORCE INDEX 或类似的索引强制提示
- 只基于现有的表结构和索引信息进行优化
- 优化后的 SQL 语句必须在语法上正确，并且可以直接执行
- 请基于 SQL 语句的实际内容进行分析，而不是基于用户的问题描述
- 用简洁明了的自然语言表达，避免技术术语过多
- 优化后的 SQL 语句必须使用格式化格式：每个子句（SELECT、FROM、JOIN、WHERE、ORDER BY 等）单独成行，关键字大写，字段名适当缩进

MySQL 特定优化要点：
1. 使用反引号 (`) 包裹包含空格或特殊字符的表名和字段名
2. 使用 LIMIT 子句限制结果行数（而不是 TOP）
3. 字符串函数：优先使用 DATE_FORMAT、CONCAT、SUBSTRING_INDEX 等 MySQL 特有函数
4. 日期时间常量使用单引号：'2024-01-01 00:00:00'
5. 避免在 WHERE 子句中对字段进行函数运算，这会导致索引失效
6. 优先使用 EXISTS 而不是 IN 来处理子查询
7. 合理使用 JOIN 代替子查询
8. 使用 EXPLAIN 分析查询执行计划（虽然在优化建议中不直接输出，但基于此思考）
9. 避免使用 SELECT *，只选择需要的字段
10. 对于 ORDER BY 和 GROUP BY，优先使用索引字段

请只返回 JSON 格式的结果，不要包含其他文字。

JSON 格式：
{{
  "optimized": true/false,
  "optimized_sql": "优化后的 SQL 语句",
  "suggestions": ["建议1", "建议2"],
  "execution_notes": "执行注释",
  "functional_description": {{
    "data_source": "涉及的表",
    "core_logic": "核心逻辑"
  }}
}}
"""


def get_postgresql_optimization_prompt(schema_text, user_query, execution_plan=None):
    """
    获取 PostgreSQL 特定的 SQL 优化提示词

    Args:
        schema_text: 数据库表结构信息
        user_query: 用户原始查询需求
        execution_plan: 数据库执行计划（可选）

    Returns:
        PostgreSQL 特定的优化提示词
    """
    execution_plan_section = ""
    if execution_plan:
        execution_plan_section = f"""
数据库执行计划：
{execution_plan}

"""
    return f"""你是一个专业的 PostgreSQL SQL 性能优化专家。请根据以下信息对给定的 SQL 语句进行性能分析和优化建议：

{schema_text}

用户原始查询需求：{user_query}

{execution_plan_section}
请分析以下 SQL 语句的性能问题，并提供具体的优化建议，包括：
1. 索引使用情况分析
2. 查询结构优化建议
3. 可能的性能瓶颈
4. 优化后的 SQL 语句

同时，请分析 SQL 语句的功能，并生成详细的功能说明，包括：
1. 数据来源：列出 SQL 语句中涉及的所有表
2. 核心逻辑：解释 SQL 语句的主要实现方法和执行流程

重要约束：
- 只能使用上述表结构信息中已有的索引，不要建议或使用不存在的索引
- 不要在优化后的 SQL 语句中使用类似的索引强制提示
- 只基于现有的表结构和索引信息进行优化
- 优化后的 SQL 语句必须在语法上正确，并且可以直接执行
- 请基于 SQL 语句的实际内容进行分析，而不是基于用户的问题描述
- 用简洁明了的自然语言表达，避免技术术语过多
- 优化后的 SQL 语句必须使用格式化格式：每个子句（SELECT、FROM、JOIN、WHERE、ORDER BY 等）单独成行，关键字大写，字段名适当缩进

PostgreSQL 特定优化要点：
1. 使用双引号 (") 包裹包含空格或特殊字符的表名和字段名（标识符）
2. 使用 LIMIT 和 OFFSET 子句实现分页
3. 字符串函数：优先使用 TO_CHAR、TO_DATE、string_agg、array_agg 等 PostgreSQL 特有函数
4. 日期时间常量使用类型转换：'2024-01-01 00:00:00'::timestamp
5. 避免在 WHERE 子句中对字段进行函数运算，这会导致索引失效
6. 优先使用 EXISTS 而不是 IN 来处理子查询
7. 合理使用 CTE（WITH 子句）提高查询可读性，但注意性能影响
8. 使用窗口函数（OVER 子句）进行复杂分析
9. 避免使用 SELECT *，只选择需要的字段
10. 对于 ORDER BY 和 GROUP BY，优先使用索引字段
11. 使用 RETURNING 子句返回插入/更新的数据
12. 考虑使用适当的 SCHEMA 限定表名

请只返回 JSON 格式的结果，不要包含其他文字。

JSON 格式：
{{
  "optimized": true/false,
  "optimized_sql": "优化后的 SQL 语句",
  "suggestions": ["建议1", "建议2"],
  "execution_notes": "执行注释",
  "functional_description": {{
    "data_source": "涉及的表",
    "core_logic": "核心逻辑"
  }}
}}
"""


def get_oracle_optimization_prompt(schema_text, user_query, execution_plan=None):
    """
    获取 Oracle 特定的 SQL 优化提示词

    Args:
        schema_text: 数据库表结构信息
        user_query: 用户原始查询需求
        execution_plan: 数据库执行计划（可选）

    Returns:
        Oracle 特定的优化提示词
    """
    execution_plan_section = ""
    if execution_plan:
        execution_plan_section = f"""
数据库执行计划：
{execution_plan}

"""
    return f"""你是一个专业的 Oracle SQL 性能优化专家。请根据以下信息对给定的 SQL 语句进行性能分析和优化建议：

{schema_text}

用户原始查询需求：{user_query}

{execution_plan_section}
请分析以下 SQL 语句的性能问题，并提供具体的优化建议，包括：
1. 索引使用情况分析
2. 查询结构优化建议
3. 可能的性能瓶颈
4. 优化后的 SQL 语句

同时，请分析 SQL 语句的功能，并生成详细的功能说明，包括：
1. 数据来源：列出 SQL 语句中涉及的所有表
2. 核心逻辑：解释 SQL 语句的主要实现方法和执行流程

重要约束：
- 只能使用上述表结构信息中已有的索引，不要建议或使用不存在的索引
- 不要在优化后的 SQL 语句中使用类似的索引强制提示
- 只基于现有的表结构和索引信息进行优化
- 优化后的 SQL 语句必须在语法上正确，并且可以直接执行
- 请基于 SQL 语句的实际内容进行分析，而不是基于用户的问题描述
- 用简洁明了的自然语言表达，避免技术术语过多
- 优化后的 SQL 语句必须使用格式化格式：每个子句（SELECT、FROM、JOIN、WHERE、ORDER BY 等）单独成行，关键字大写，字段名适当缩进

Oracle 特定优化要点：
1. 使用双引号 (") 包裹包含空格或特殊字符的表名和字段名（标识符）
2. 使用 ROWNUM 伪列限制结果行数，或者在 Oracle 12c+ 中使用 FETCH FIRST n ROWS ONLY
3. 字符串函数：优先使用 TO_CHAR、TO_DATE、CONCAT、SUBSTR 等 Oracle 特有函数
4. 日期时间常量使用 DATE 或 TIMESTAMP 关键字：DATE '2024-01-01' 或 TIMESTAMP '2024-01-01 00:00:00'
5. 避免在 WHERE 子句中对字段进行函数运算，这会导致索引失效
6. 优先使用 EXISTS 而不是 IN 来处理子查询
7. 合理使用 WITH 子句（子查询分解）提高查询可读性
8. 使用窗口函数（OVER 子句）进行复杂分析
9. 避免使用 SELECT *，只选择需要的字段
10. 对于 ORDER BY 和 GROUP BY，优先使用索引字段
11. 使用 || 运算符连接字符串
12. 使用 DUAL 表进行单值查询
13. 使用 SYSDATE、SYSTIMESTAMP 获取当前时间
14. 考虑使用适当的 HINT 进行优化（但建议不要强制使用）

请只返回 JSON 格式的结果，不要包含其他文字。

JSON 格式：
{{
  "optimized": true/false,
  "optimized_sql": "优化后的 SQL 语句",
  "suggestions": ["建议1", "建议2"],
  "execution_notes": "执行注释",
  "functional_description": {{
    "data_source": "涉及的表",
    "core_logic": "核心逻辑"
  }}
}}
"""


def get_sqlserver_optimization_prompt(schema_text, user_query, execution_plan=None):
    """
    获取 SQL Server 特定的 SQL 优化提示词

    Args:
        schema_text: 数据库表结构信息
        user_query: 用户原始查询需求
        execution_plan: 数据库执行计划（可选）

    Returns:
        SQL Server 特定的优化提示词
    """
    execution_plan_section = ""
    if execution_plan:
        execution_plan_section = f"""
数据库执行计划：
{execution_plan}

"""
    return f"""你是一个专业的 SQL Server SQL 性能优化专家。请根据以下信息对给定的 SQL 语句进行性能分析和优化建议：

{schema_text}

用户原始查询需求：{user_query}

{execution_plan_section}
请分析以下 SQL 语句的性能问题，并提供具体的优化建议，包括：
1. 索引使用情况分析
2. 查询结构优化建议
3. 可能的性能瓶颈
4. 优化后的 SQL 语句

同时，请分析 SQL 语句的功能，并生成详细的功能说明，包括：
1. 数据来源：列出 SQL 语句中涉及的所有表
2. 核心逻辑：解释 SQL 语句的主要实现方法和执行流程

重要约束：
- 只能使用上述表结构信息中已有的索引，不要建议或使用不存在的索引
- 不要在优化后的 SQL 语句中使用类似的索引强制提示
- 只基于现有的表结构和索引信息进行优化
- 优化后的 SQL 语句必须在语法上正确，并且可以直接执行
- 请基于 SQL 语句的实际内容进行分析，而不是基于用户的问题描述
- 用简洁明了的自然语言表达，避免技术术语过多
- 优化后的 SQL 语句必须使用格式化格式：每个子句（SELECT、FROM、JOIN、WHERE、ORDER BY 等）单独成行，关键字大写，字段名适当缩进
- 特别注意：当使用 GROUP BY 子句时，SELECT 列表中的所有非聚合列必须包含在 GROUP BY 子句中，即使这些列在功能上依赖于主键

SQL Server 特定优化要点：
1. 使用方括号 ([]) 包裹包含空格或特殊字符的表名和字段名
2. 中文别名必须加方括号：SELECT name AS [姓名]
3. 使用 TOP 子句限制结果行数（而不是 LIMIT）
4. 使用 OFFSET ... FETCH NEXT 子句实现分页（SQL Server 2012+）
5. 字符串函数：优先使用 CONVERT、CAST、STUFF、CHARINDEX 等 SQL Server 特有函数
6. 字符串常量使用单引号，N 前缀表示 Unicode：N'中文值'
7. 日期时间常量使用单引号：'2024-01-01'
8. 避免在 WHERE 子句中对字段进行函数运算，这会导致索引失效
9. 优先使用 EXISTS 而不是 IN 来处理子查询
10. 合理使用 CTE（WITH 子句）提高查询可读性
11. 使用窗口函数（OVER 子句）进行复杂分析
12. 避免使用 SELECT *，只选择需要的字段
13. 对于 ORDER BY 和 GROUP BY，优先使用索引字段
14. 使用 GETDATE()、SYSDATETIME() 获取当前时间
15. 使用 OUTPUT 子句返回插入/更新的数据
16. 避免使用 MySQL 特有的语法（如 LIMIT、反引号）

请只返回 JSON 格式的结果，不要包含其他文字。

JSON 格式：
{{
  "optimized": true/false,
  "optimized_sql": "优化后的 SQL 语句",
  "suggestions": ["建议1", "建议2"],
  "execution_notes": "执行注释",
  "functional_description": {{
    "data_source": "涉及的表",
    "core_logic": "核心逻辑"
  }}
}}
"""


def get_optimization_prompt_by_db_type(db_type, schema_text, user_query, execution_plan=None):
    """
    根据数据库类型获取对应的优化提示词

    Args:
        db_type: 数据库类型
        schema_text: 数据库表结构信息
        user_query: 用户原始查询需求
        execution_plan: 数据库执行计划（可选）

    Returns:
        对应数据库类型的优化提示词
    """
    db_type_lower = db_type.lower()
    
    if db_type_lower == 'mysql':
        logger.info("使用 MySQL 优化提示词")
        return get_mysql_optimization_prompt(schema_text, user_query, execution_plan)
    elif db_type_lower in ['pg', 'postgresql']:
        logger.info("使用 PostgreSQL 优化提示词")
        return get_postgresql_optimization_prompt(schema_text, user_query, execution_plan)
    elif db_type_lower == 'oracle':
        logger.info("使用 Oracle 优化提示词")
        return get_oracle_optimization_prompt(schema_text, user_query, execution_plan)
    elif db_type_lower in ['sqlserver', 'sql_server', 'mssql']:
        logger.info("使用 SQL Server 优化提示词")
        return get_sqlserver_optimization_prompt(schema_text, user_query, execution_plan)
    else:
        logger.warning(f"未知数据库类型: {db_type}，默认使用 MySQL 优化提示词")
        return get_mysql_optimization_prompt(schema_text, user_query, execution_plan)
