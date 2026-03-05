import logging
import pymysql
import psycopg2
import pyodbc
from psycopg2 import OperationalError

logger = logging.getLogger(__name__)


class BaseDatabaseHandler:
    """数据库处理器基类"""

    def __init__(self, config):
        self.config = config

    def test_connection(self):
        """测试数据库连接"""
        raise NotImplementedError

    def get_tables(self):
        """获取表列表，返回 [{'tableName': name, 'tableComment': comment}]"""
        raise NotImplementedError

    def get_table_fields(self, table_name):
        """获取表字段信息"""
        raise NotImplementedError

    def get_table_indexes(self, table_name):
        """获取表索引信息"""
        raise NotImplementedError

    def get_table_comment(self, table_name):
        """获取表注释"""
        raise NotImplementedError


class MySQLHandler(BaseDatabaseHandler):
    """MySQL数据库处理器"""

    def test_connection(self):
        connection = None
        try:
            connection = pymysql.connect(
                host=self.config['host'],
                port=int(self.config.get('port', 3306)),
                user=self.config['username'],
                password=self.config['password'],
                database=self.config['database'],
                charset='utf8mb4',
                connect_timeout=10
            )
            return True
        except Exception as e:
            logger.error("MySQL连接失败: %s", e)
            raise
        finally:
            if connection:
                connection.close()

    def get_tables(self):
        tables = []
        connection = None
        try:
            connection = pymysql.connect(
                host=self.config['host'],
                port=int(self.config.get('port', 3306)),
                user=self.config['username'],
                password=self.config['password'],
                database=self.config['database'],
                charset='utf8mb4'
            )
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES FROM `{}`".format(self.config['database']))
                all_tables = cursor.fetchall()

                for table in all_tables:
                    table_name = table[0]
                    cursor.execute("""
                        SELECT TABLE_COMMENT 
                        FROM information_schema.TABLES 
                        WHERE TABLE_SCHEMA = '{}' 
                        AND TABLE_NAME = '{}'
                    """.format(self.config['database'], table_name))
                    comment_result = cursor.fetchone()
                    table_comment = comment_result[0] if comment_result else ''
                    tables.append({
                        'tableName': table_name,
                        'tableComment': table_comment
                    })
            return tables
        finally:
            if connection:
                connection.close()

    def get_table_fields(self, table_name):
        fields = []
        connection = None
        try:
            connection = pymysql.connect(
                host=self.config['host'],
                port=int(self.config.get('port', 3306)),
                user=self.config['username'],
                password=self.config['password'],
                database=self.config['database'],
                charset='utf8mb4'
            )
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        COLUMN_NAME,
                        COLUMN_TYPE,
                        COLUMN_COMMENT,
                        ORDINAL_POSITION
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = '{}' 
                    AND TABLE_NAME = '{}'
                    ORDER BY ORDINAL_POSITION
                """.format(self.config['database'], table_name))
                field_results = cursor.fetchall()

                for field in field_results:
                    fields.append({
                        'field_name': field[0],
                        'field_type': field[1],
                        'field_comment': field[2] if field[2] else '',
                        'field_index': field[3]
                    })
            return fields
        finally:
            if connection:
                connection.close()

    def get_table_indexes(self, table_name):
        indexes = []
        connection = None
        try:
            connection = pymysql.connect(
                host=self.config['host'],
                port=int(self.config.get('port', 3306)),
                user=self.config['username'],
                password=self.config['password'],
                database=self.config['database'],
                charset='utf8mb4'
            )
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        INDEX_NAME,
                        COLUMN_NAME,
                        NON_UNIQUE,
                        SEQ_IN_INDEX,
                        INDEX_TYPE
                    FROM information_schema.STATISTICS
                    WHERE TABLE_SCHEMA = '{}' 
                    AND TABLE_NAME = '{}'
                    ORDER BY INDEX_NAME, SEQ_IN_INDEX
                """.format(self.config['database'], table_name))
                index_results = cursor.fetchall()

                for index in index_results:
                    index_type = "PRIMARY" if index[0] == "PRIMARY" else "UNIQUE" if index[2] == 0 else "INDEX"
                    indexes.append({
                        'index_name': index[0],
                        'column_name': index[1],
                        'non_unique': index[2],
                        'seq_in_index': index[3],
                        'index_type': index_type
                    })
            return indexes
        finally:
            if connection:
                connection.close()

    def get_table_comment(self, table_name):
        connection = None
        try:
            connection = pymysql.connect(
                host=self.config['host'],
                port=int(self.config.get('port', 3306)),
                user=self.config['username'],
                password=self.config['password'],
                database=self.config['database'],
                charset='utf8mb4'
            )
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT TABLE_COMMENT 
                    FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = '{}' 
                    AND TABLE_NAME = '{}'
                """.format(self.config['database'], table_name))
                comment_result = cursor.fetchone()
                return comment_result[0] if comment_result else ''
        finally:
            if connection:
                connection.close()


class PostgreSQLHandler(BaseDatabaseHandler):
    """PostgreSQL数据库处理器"""

    def test_connection(self):
        connection = None
        try:
            connection = psycopg2.connect(
                host=self.config['host'],
                port=int(self.config.get('port', 5432)),
                user=self.config['username'],
                password=self.config['password'],
                dbname=self.config['database'],
                connect_timeout=10
            )
            return True
        except OperationalError as e:
            logger.error("PostgreSQL连接失败: %s", e)
            raise
        finally:
            if connection:
                connection.close()

    def get_tables(self):
        tables = []
        connection = None
        schema = self.config.get('dbSchema', 'public')
        try:
            connection = psycopg2.connect(
                host=self.config['host'],
                port=int(self.config.get('port', 5432)),
                user=self.config['username'],
                password=self.config['password'],
                dbname=self.config['database']
            )
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        c.relname AS tablename,
                        obj_description(c.oid) AS tablecomment
                    FROM pg_catalog.pg_class c
                    INNER JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
                    WHERE n.nspname = %s
                    AND c.relkind = 'r'
                    ORDER BY tablename
                """, (schema,))
                all_tables = cursor.fetchall()

                for table in all_tables:
                    table_name = table[0]
                    table_comment = table[1] if table[1] else ''
                    tables.append({
                        'tableName': table_name,
                        'tableComment': table_comment
                    })
            return tables
        finally:
            if connection:
                connection.close()

    def get_table_fields(self, table_name):
        fields = []
        connection = None
        schema = self.config.get('dbSchema', 'public')
        try:
            connection = psycopg2.connect(
                host=self.config['host'],
                port=int(self.config.get('port', 5432)),
                user=self.config['username'],
                password=self.config['password'],
                dbname=self.config['database']
            )
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        a.attname AS column_name,
                        pg_catalog.format_type(a.atttypid, a.atttypmod) AS column_type,
                        col_description(a.attrelid, a.attnum) AS column_comment,
                        a.attnum AS ordinal_position
                    FROM pg_catalog.pg_attribute a
                    INNER JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
                    INNER JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
                    WHERE n.nspname = %s
                    AND c.relname = %s
                    AND a.attnum > 0
                    AND NOT a.attisdropped
                    ORDER BY a.attnum
                """, (schema, table_name))
                field_results = cursor.fetchall()

                for field in field_results:
                    fields.append({
                        'field_name': field[0],
                        'field_type': field[1],
                        'field_comment': field[2] if field[2] else '',
                        'field_index': field[3]
                    })
            return fields
        finally:
            if connection:
                connection.close()

    def get_table_indexes(self, table_name):
        indexes = []
        connection = None
        schema = self.config.get('dbSchema', 'public')
        try:
            connection = psycopg2.connect(
                host=self.config['host'],
                port=int(self.config.get('port', 5432)),
                user=self.config['username'],
                password=self.config['password'],
                dbname=self.config['database']
            )
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        i.relname AS index_name,
                        a.attname AS column_name,
                        idx.indisunique AS non_unique,
                        ARRAY_POSITION(idx.indkey, a.attnum) AS seq_in_index,
                        CASE 
                            WHEN idx.indisprimary THEN 'PRIMARY'
                            WHEN idx.indisunique THEN 'UNIQUE'
                            ELSE 'INDEX'
                        END AS index_type
                    FROM pg_index idx
                    JOIN pg_class i ON idx.indexrelid = i.oid
                    JOIN pg_class t ON idx.indrelid = t.oid
                    JOIN pg_namespace n ON t.relnamespace = n.oid
                    JOIN pg_attribute a ON a.attrelid = t.oid
                    WHERE n.nspname = %s
                    AND t.relname = %s
                    AND a.attnum = ANY(idx.indkey)
                    ORDER BY i.relname, seq_in_index
                """, (schema, table_name))
                index_results = cursor.fetchall()

                for index in index_results:
                    indexes.append({
                        'index_name': index[0],
                        'column_name': index[1],
                        'non_unique': 0 if index[2] else 1,
                        'seq_in_index': index[3],
                        'index_type': index[4]
                    })
            return indexes
        finally:
            if connection:
                connection.close()

    def get_table_comment(self, table_name):
        connection = None
        schema = self.config.get('dbSchema', 'public')
        try:
            connection = psycopg2.connect(
                host=self.config['host'],
                port=int(self.config.get('port', 5432)),
                user=self.config['username'],
                password=self.config['password'],
                dbname=self.config['database']
            )
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT obj_description(c.oid)
                    FROM pg_catalog.pg_class c
                    INNER JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
                    WHERE n.nspname = %s
                    AND c.relname = %s
                """, (schema, table_name))
                comment_result = cursor.fetchone()
                return comment_result[0] if comment_result and comment_result[0] else ''
        finally:
            if connection:
                connection.close()


class SQLServerHandler(BaseDatabaseHandler):
    """SQL Server数据库处理器"""

    def test_connection(self):
        connection = None
        try:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.config['host']},{self.config.get('port', 1433)};"
                f"DATABASE={self.config['database']};"
                f"UID={self.config['username']};"
                f"PWD={self.config['password']};"
                f"TrustServerCertificate=yes;"
            )
            connection = pyodbc.connect(conn_str, timeout=10)
            return True
        except Exception as e:
            logger.error("SQL Server连接失败: %s", e)
            raise
        finally:
            if connection:
                connection.close()

    def get_tables(self):
        tables = []
        connection = None
        schema = self.config.get('dbSchema', 'dbo')
        try:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.config['host']},{self.config.get('port', 1433)};"
                f"DATABASE={self.config['database']};"
                f"UID={self.config['username']};"
                f"PWD={self.config['password']};"
                f"TrustServerCertificate=yes;"
            )
            connection = pyodbc.connect(conn_str)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        t.TABLE_NAME,
                        ISNULL(p.value, '') AS TABLE_COMMENT
                    FROM INFORMATION_SCHEMA.TABLES t
                    LEFT JOIN sys.extended_properties p 
                        ON p.major_id = OBJECT_ID(t.TABLE_SCHEMA + '.' + t.TABLE_NAME)
                        AND p.minor_id = 0
                        AND p.name = 'MS_Description'
                    WHERE t.TABLE_TYPE = 'BASE TABLE'
                    AND t.TABLE_SCHEMA = ?
                    ORDER BY t.TABLE_NAME
                """, (schema,))
                all_tables = cursor.fetchall()

                for table in all_tables:
                    tables.append({
                        'tableName': table[0],
                        'tableComment': table[1] if table[1] else ''
                    })
            return tables
        finally:
            if connection:
                connection.close()

    def get_table_fields(self, table_name):
        fields = []
        connection = None
        schema = self.config.get('dbSchema', 'dbo')
        try:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.config['host']},{self.config.get('port', 1433)};"
                f"DATABASE={self.config['database']};"
                f"UID={self.config['username']};"
                f"PWD={self.config['password']};"
                f"TrustServerCertificate=yes;"
            )
            connection = pyodbc.connect(conn_str)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        c.COLUMN_NAME,
                        c.DATA_TYPE + 
                            CASE 
                                WHEN c.CHARACTER_MAXIMUM_LENGTH IS NOT NULL 
                                THEN '(' + CAST(c.CHARACTER_MAXIMUM_LENGTH AS VARCHAR) + ')'
                                ELSE ''
                            END AS COLUMN_TYPE,
                        ISNULL(p.value, '') AS COLUMN_COMMENT,
                        c.ORDINAL_POSITION
                    FROM INFORMATION_SCHEMA.COLUMNS c
                    LEFT JOIN sys.extended_properties p 
                        ON p.major_id = OBJECT_ID(c.TABLE_SCHEMA + '.' + c.TABLE_NAME)
                        AND p.minor_id = c.ORDINAL_POSITION
                        AND p.name = 'MS_Description'
                    WHERE c.TABLE_SCHEMA = ?
                    AND c.TABLE_NAME = ?
                    ORDER BY c.ORDINAL_POSITION
                """, (schema, table_name))
                field_results = cursor.fetchall()

                for field in field_results:
                    fields.append({
                        'field_name': field[0],
                        'field_type': field[1],
                        'field_comment': field[2] if field[2] else '',
                        'field_index': field[3]
                    })
            return fields
        finally:
            if connection:
                connection.close()

    def get_table_indexes(self, table_name):
        indexes = []
        connection = None
        schema = self.config.get('dbSchema', 'dbo')
        try:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.config['host']},{self.config.get('port', 1433)};"
                f"DATABASE={self.config['database']};"
                f"UID={self.config['username']};"
                f"PWD={self.config['password']};"
                f"TrustServerCertificate=yes;"
            )
            connection = pyodbc.connect(conn_str)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        i.name AS index_name,
                        col.name AS column_name,
                        i.is_unique AS non_unique,
                        ic.key_ordinal AS seq_in_index,
                        CASE 
                            WHEN i.is_primary_key = 1 THEN 'PRIMARY'
                            WHEN i.is_unique = 1 THEN 'UNIQUE'
                            ELSE 'INDEX'
                        END AS index_type
                    FROM sys.indexes i
                    INNER JOIN sys.index_columns ic 
                        ON i.object_id = ic.object_id 
                        AND i.index_id = ic.index_id
                    INNER JOIN sys.columns col 
                        ON ic.object_id = col.object_id 
                        AND ic.column_id = col.column_id
                    INNER JOIN sys.tables t 
                        ON i.object_id = t.object_id
                    INNER JOIN sys.schemas s 
                        ON t.schema_id = s.schema_id
                    WHERE s.name = ?
                    AND t.name = ?
                    AND i.type IN (1, 2)
                    ORDER BY i.name, ic.key_ordinal
                """, (schema, table_name))
                index_results = cursor.fetchall()

                for index in index_results:
                    indexes.append({
                        'index_name': index[0],
                        'column_name': index[1],
                        'non_unique': 0 if index[2] else 1,
                        'seq_in_index': index[3],
                        'index_type': index[4]
                    })
            return indexes
        finally:
            if connection:
                connection.close()

    def get_table_comment(self, table_name):
        connection = None
        schema = self.config.get('dbSchema', 'dbo')
        try:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.config['host']},{self.config.get('port', 1433)};"
                f"DATABASE={self.config['database']};"
                f"UID={self.config['username']};"
                f"PWD={self.config['password']};"
                f"TrustServerCertificate=yes;"
            )
            connection = pyodbc.connect(conn_str)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT ISNULL(p.value, '') AS TABLE_COMMENT
                    FROM sys.tables t
                    INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
                    LEFT JOIN sys.extended_properties p 
                        ON p.major_id = t.object_id
                        AND p.minor_id = 0
                        AND p.name = 'MS_Description'
                    WHERE s.name = ?
                    AND t.name = ?
                """, (schema, table_name))
                comment_result = cursor.fetchone()
                return comment_result[0] if comment_result and comment_result[0] else ''
        finally:
            if connection:
                connection.close()


def get_database_handler(db_type, config):
    """
    获取数据库处理器

    Args:
        db_type: 数据库类型 (mysql, pg, postgresql, sqlserver, sqlServer等)

    Returns:
        对应的数据库处理器实例
    """
    db_type = db_type.lower()

    if db_type == 'mysql':
        return MySQLHandler(config)
    elif db_type in ['pg', 'postgresql']:
        return PostgreSQLHandler(config)
    elif db_type in ['sqlserver', 'sql_server', 'mssql']:
        return SQLServerHandler(config)
    else:
        raise ValueError("不支持的数据库类型: {}".format(db_type))

