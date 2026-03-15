import logging

logger = logging.getLogger(__name__)


def get_mysql_validation_prompt(
    schema_text: str,
    user_query: str,
    db_errors_text: str
) -> str:
    """
    获取 MySQL 特定的 SQL 验证和修复提示词

    Args:
        schema_text: 数据库表结构信息
        user_query: 用户查询需求
        db_errors_text: 数据库验证错误信息

    Returns:
        MySQL 特定的系统提示词
    """
    return f"""你是一个专业的 MySQL SQL 验证和修复专家。请分析并修复给定的 MySQL SQL 语句。

{schema_text}

用户查询需求：{user_query}{db_errors_text}

任务要求：
1. 语法正确性：检查 SQL 语法是否符合 MySQL 规范
2. 表名正确性：检查引用的表名是否存在于 schema 中
3. 字段正确性：检查引用的字段名是否正确
4. 逻辑合理性：检查 SQL 是否合理满足用户需求
5. 如果发现问题（包括数据库验证错误），请直接修复并返回修复后的 MySQL 语法的 SQL
6. 如果 SQL 正确，请原样返回

MySQL 修复要点：
- 使用 LIMIT 代替 TOP
- 使用反引号 (`) 包裹标识符
- 使用 MySQL 特有的函数（DATE_FORMAT、CONCAT 等）
- 使用 AUTO_INCREMENT 定义自增字段

请只返回 JSON 格式的验证修复结果，不要包含其他文字。

JSON 格式：
{{
  "is_valid": true/false,
  "llm_validation_passed": true/false,
  "original_sql": "原始 SQL",
  "fixed_sql": "修复后的 SQL（如果需要）",
  "errors": ["错误信息1", "错误信息2"],
  "warnings": ["警告信息1", "警告信息2"],
  "llm_feedback": "详细的验证反馈和修复说明"
}}

如果 SQL 基本正确但有改进空间，请设置 is_valid=true 但在 warnings 中给出建议。
如果 SQL 存在严重错误，请设置 is_valid=false 并在 errors 中说明原因，同时提供修复后的 SQL。"""


def get_postgresql_validation_prompt(
    schema_text: str,
    user_query: str,
    db_errors_text: str
) -> str:
    """
    获取 PostgreSQL 特定的 SQL 验证和修复提示词

    Args:
        schema_text: 数据库表结构信息
        user_query: 用户查询需求
        db_errors_text: 数据库验证错误信息

    Returns:
        PostgreSQL 特定的系统提示词
    """
    return f"""你是一个专业的 PostgreSQL SQL 验证和修复专家。请分析并修复给定的 PostgreSQL SQL 语句。

{schema_text}

用户查询需求：{user_query}{db_errors_text}

任务要求：
1. 语法正确性：检查 SQL 语法是否符合 PostgreSQL 规范
2. 表名正确性：检查引用的表名是否存在于 schema 中
3. 字段正确性：检查引用的字段名是否正确
4. 逻辑合理性：检查 SQL 是否合理满足用户需求
5. 如果发现问题（包括数据库验证错误），请直接修复并返回修复后的 PostgreSQL 语法的 SQL
6. 如果 SQL 正确，请原样返回

PostgreSQL 修复要点：
- 使用双引号 (") 包裹标识符
- 使用 LIMIT 限制结果
- 使用 PostgreSQL 特有的函数（TO_CHAR、string_agg、array_agg 等）
- 使用 SERIAL 或 BIGSERIAL 定义自增字段
- 使用 WITH 子句（CTE）
- 使用 RETURNING 子句

请只返回 JSON 格式的验证修复结果，不要包含其他文字。

JSON 格式：
{{
  "is_valid": true/false,
  "llm_validation_passed": true/false,
  "original_sql": "原始 SQL",
  "fixed_sql": "修复后的 SQL（如果需要）",
  "errors": ["错误信息1", "错误信息2"],
  "warnings": ["警告信息1", "警告信息2"],
  "llm_feedback": "详细的验证反馈和修复说明"
}}

如果 SQL 基本正确但有改进空间，请设置 is_valid=true 但在 warnings 中给出建议。
如果 SQL 存在严重错误，请设置 is_valid=false 并在 errors 中说明原因，同时提供修复后的 SQL。"""


def get_oracle_validation_prompt(
    schema_text: str,
    user_query: str,
    db_errors_text: str
) -> str:
    """
    获取 Oracle 特定的 SQL 验证和修复提示词

    Args:
        schema_text: 数据库表结构信息
        user_query: 用户查询需求
        db_errors_text: 数据库验证错误信息

    Returns:
        Oracle 特定的系统提示词
    """
    return f"""你是一个专业的 Oracle SQL 验证和修复专家。请分析并修复给定的 Oracle SQL 语句。

{schema_text}

用户查询需求：{user_query}{db_errors_text}

任务要求：
1. 语法正确性：检查 SQL 语法是否符合 Oracle 规范
2. 表名正确性：检查引用的表名是否存在于 schema 中
3. 字段正确性：检查引用的字段名是否正确
4. 逻辑合理性：检查 SQL 是否合理满足用户需求
5. 如果发现问题（包括数据库验证错误），请直接修复并返回修复后的 Oracle 语法的 SQL
6. 如果 SQL 正确，请原样返回

Oracle 修复要点：
- 使用双引号 (") 包裹标识符
- 使用 ROWNUM 或 FETCH FIRST n ROWS ONLY 限制结果
- 使用 Oracle 特有的函数（TO_CHAR、TO_DATE、SUBSTR 等）
- 使用 SEQUENCE 生成自增值
- 使用 || 运算符连接字符串
- 使用 DUAL 表进行单值查询
- 使用 SYSDATE、SYSTIMESTAMP 获取当前时间

请只返回 JSON 格式的验证修复结果，不要包含其他文字。

JSON 格式：
{{
  "is_valid": true/false,
  "llm_validation_passed": true/false,
  "original_sql": "原始 SQL",
  "fixed_sql": "修复后的 SQL（如果需要）",
  "errors": ["错误信息1", "错误信息2"],
  "warnings": ["警告信息1", "警告信息2"],
  "llm_feedback": "详细的验证反馈和修复说明"
}}

如果 SQL 基本正确但有改进空间，请设置 is_valid=true 但在 warnings 中给出建议。
如果 SQL 存在严重错误，请设置 is_valid=false 并在 errors 中说明原因，同时提供修复后的 SQL。"""


def get_sqlserver_validation_prompt(
    schema_text: str,
    user_query: str,
    db_errors_text: str
) -> str:
    """
    获取 SQL Server 特定的 SQL 验证和修复提示词

    Args:
        schema_text: 数据库表结构信息
        user_query: 用户查询需求
        db_errors_text: 数据库验证错误信息

    Returns:
        SQL Server 特定的系统提示词
    """
    return f"""你是一个专业的 SQL Server SQL 验证和修复专家。请分析并修复给定的 SQL Server SQL 语句。

{schema_text}

用户查询需求：{user_query}{db_errors_text}

任务要求：
1. 语法正确性：检查 SQL 语法是否符合 SQL Server 规范
2. 表名正确性：检查引用的表名是否存在于 schema 中
3. 字段正确性：检查引用的字段名是否正确
4. 逻辑合理性：检查 SQL 是否合理满足用户需求
5. 如果发现问题（包括数据库验证错误），请直接修复并返回修复后的 SQL Server 语法的 SQL
6. 如果 SQL 正确，请原样返回

SQL Server 修复要点：
- 使用方括号 ([]) 包裹标识符（包括中文别名）
- 使用 TOP 子句代替 LIMIT
- 使用 N 前缀表示 Unicode 字符串
- 使用 SQL Server 特有的函数（CONVERT、CAST、STUFF、CHARINDEX 等）
- 使用 IDENTITY 定义自增字段
- 使用 OFFSET ... FETCH NEXT 实现分页（SQL Server 2012+）
- 使用 OUTPUT 子句返回插入/更新的数据
- 使用 GETDATE()、SYSDATETIME() 获取当前时间
- 使用 GROUP BY 时，SELECT 列表中的所有非聚合列必须包含在 GROUP BY 中
- 避免使用 MySQL 特有的语法（如 LIMIT、反引号）

请只返回 JSON 格式的验证修复结果，不要包含其他文字。

JSON 格式：
{{
  "is_valid": true/false,
  "llm_validation_passed": true/false,
  "original_sql": "原始 SQL",
  "fixed_sql": "修复后的 SQL（如果需要）",
  "errors": ["错误信息1", "错误信息2"],
  "warnings": ["警告信息1", "警告信息2"],
  "llm_feedback": "详细的验证反馈和修复说明"
}}

如果 SQL 基本正确但有改进空间，请设置 is_valid=true 但在 warnings 中给出建议。
如果 SQL 存在严重错误，请设置 is_valid=false 并在 errors 中说明原因，同时提供修复后的 SQL。"""


def get_validation_prompt_by_db_type(
    db_type: str,
    schema_text: str,
    user_query: str,
    db_errors_text: str
) -> str:
    """
    根据数据库类型获取对应的验证和修复提示词

    Args:
        db_type: 数据库类型
        schema_text: 数据库表结构信息
        user_query: 用户查询需求
        db_errors_text: 数据库验证错误信息

    Returns:
        对应数据库类型的验证和修复提示词
    """
    db_type_lower = db_type.lower()
    
    if db_type_lower == 'mysql':
        logger.info("使用 MySQL 验证修复提示词")
        return get_mysql_validation_prompt(schema_text, user_query, db_errors_text)
    elif db_type_lower in ['pg', 'postgresql']:
        logger.info("使用 PostgreSQL 验证修复提示词")
        return get_postgresql_validation_prompt(schema_text, user_query, db_errors_text)
    elif db_type_lower == 'oracle':
        logger.info("使用 Oracle 验证修复提示词")
        return get_oracle_validation_prompt(schema_text, user_query, db_errors_text)
    elif db_type_lower in ['sqlserver', 'sql_server', 'mssql']:
        logger.info("使用 SQL Server 验证修复提示词")
        return get_sqlserver_validation_prompt(schema_text, user_query, db_errors_text)
    else:
        logger.warning(f"未知数据库类型: {db_type}，默认使用 MySQL 验证修复提示词")
        return get_mysql_validation_prompt(schema_text, user_query, db_errors_text)
