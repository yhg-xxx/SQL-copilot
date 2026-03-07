import logging
import os
import pymysql
import psycopg2
import pyodbc
import oracledb
from typing import Dict, Any

logger = logging.getLogger(__name__)


class BaseDBVerifierExecutor:
    """数据库验证和执行基类"""

    def __init__(self, config):
        self.config = config

    def validate_sql(self, sql: str) -> Dict[str, Any]:
        """验证 SQL 语句"""
        raise NotImplementedError

    def execute_sql(self, sql: str) -> Dict[str, Any]:
        """执行 SQL 语句"""
        raise NotImplementedError


class MySQLVerifierExecutor(BaseDBVerifierExecutor):
    """MySQL 数据库验证和执行器"""

    def validate_sql(self, sql: str) -> Dict[str, Any]:
        """使用 MySQL 验证 SQL 语句"""
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "validation_passed": False,
            "explain_result": None
        }

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

            cursor = None
            try:
                cursor = connection.cursor()
                clean_sql = sql.strip().rstrip(';')
                explain_sql = f"EXPLAIN {clean_sql}"
                logger.info(f"执行 EXPLAIN: {explain_sql}")
                cursor.execute(explain_sql)
                explain_result = cursor.fetchall()
                result["explain_result"] = str(explain_result)

                if "LIMIT" not in sql.upper():
                    validation_sql = f"{clean_sql} LIMIT 10"
                else:
                    validation_sql = clean_sql
                cursor.execute(validation_sql)
                if hasattr(cursor, 'with_rows') and cursor.with_rows:
                    cursor.fetchall()

                result["validation_passed"] = True
                result["warnings"].append("MySQL 验证通过")
                result["valid"] = True

            except Exception as e:
                logger.error(f"MySQL 验证失败: {e}")
                result["errors"].append(f"验证失败: {str(e)}")
            finally:
                if cursor:
                    cursor.close()
                connection.close()

        except Exception as e:
            logger.error(f"MySQL 连接失败: {e}")
            result["errors"].append(f"连接失败: {str(e)}")

        return result

    def execute_sql(self, sql: str) -> Dict[str, Any]:
        """使用 MySQL 执行 SQL 语句"""
        result = {
            "success": False,
            "data": None,
            "columns": None,
            "row_count": 0,
            "error": None
        }

        try:
            connection = pymysql.connect(
                host=self.config['host'],
                port=int(self.config.get('port', 3306)),
                user=self.config['username'],
                password=self.config['password'],
                database=self.config['database'],
                charset='utf8mb4',
                connect_timeout=30
            )

            cursor = None
            try:
                cursor = connection.cursor(pymysql.cursors.DictCursor)
                clean_sql = sql.strip().rstrip(';')

                if "LIMIT" not in sql.upper():
                    execution_sql = f"{clean_sql} LIMIT 1000"
                else:
                    execution_sql = clean_sql

                logger.info(f"执行 SQL: {execution_sql}")
                cursor.execute(execution_sql)

                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    result["columns"] = columns
                    # 直接获取数据，不检查 with_rows
                    data = cursor.fetchall()
                    result["data"] = list(data) if data else []
                    result["row_count"] = len(result["data"])
                    logger.info(f"查询返回 {result['row_count']} 条数据")

                result["success"] = True

            except Exception as e:
                logger.error(f"MySQL 执行失败: {e}")
                result["error"] = f"执行失败: {str(e)}"
            finally:
                if cursor:
                    cursor.close()
                connection.close()

        except Exception as e:
            logger.error(f"MySQL 连接失败: {e}")
            result["error"] = f"连接失败: {str(e)}"

        return result


class PostgreSQLVerifierExecutor(BaseDBVerifierExecutor):
    """PostgreSQL 数据库验证和执行器"""

    def validate_sql(self, sql: str) -> Dict[str, Any]:
        """使用 PostgreSQL 验证 SQL 语句"""
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "validation_passed": False,
            "explain_result": None
        }

        try:
            schema = self.config.get('db_schema', 'public')
            connection = psycopg2.connect(
                host=self.config['host'],
                port=int(self.config.get('port', 5432)),
                user=self.config['username'],
                password=self.config['password'],
                dbname=self.config['database'],
                connect_timeout=10
            )

            cursor = None
            try:
                cursor = connection.cursor()
                clean_sql = sql.strip().rstrip(';')
                explain_sql = f"EXPLAIN {clean_sql}"
                logger.info(f"执行 EXPLAIN: {explain_sql}")
                cursor.execute(explain_sql)
                explain_result = cursor.fetchall()
                result["explain_result"] = str(explain_result)

                if "LIMIT" not in sql.upper():
                    validation_sql = f"{clean_sql} LIMIT 10"
                else:
                    validation_sql = clean_sql
                cursor.execute(validation_sql)
                if cursor.description:
                    cursor.fetchall()

                result["validation_passed"] = True
                result["warnings"].append("PostgreSQL 验证通过")
                result["valid"] = True

            except Exception as e:
                logger.error(f"PostgreSQL 验证失败: {e}")
                result["errors"].append(f"验证失败: {str(e)}")
            finally:
                if cursor:
                    cursor.close()
                connection.close()

        except Exception as e:
            logger.error(f"PostgreSQL 连接失败: {e}")
            result["errors"].append(f"连接失败: {str(e)}")

        return result

    def execute_sql(self, sql: str) -> Dict[str, Any]:
        """使用 PostgreSQL 执行 SQL 语句"""
        result = {
            "success": False,
            "data": None,
            "columns": None,
            "row_count": 0,
            "error": None
        }

        try:
            schema = self.config.get('db_schema', 'public')
            connection = psycopg2.connect(
                host=self.config['host'],
                port=int(self.config.get('port', 5432)),
                user=self.config['username'],
                password=self.config['password'],
                dbname=self.config['database'],
                connect_timeout=30
            )

            cursor = None
            try:
                cursor = connection.cursor()
                clean_sql = sql.strip().rstrip(';')

                if "LIMIT" not in sql.upper():
                    execution_sql = f"{clean_sql} LIMIT 1000"
                else:
                    execution_sql = clean_sql

                logger.info(f"执行 SQL: {execution_sql}")
                cursor.execute(execution_sql)

                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    result["columns"] = columns

                if cursor.description:
                    data = []
                    columns = [desc[0] for desc in cursor.description]
                    for row in cursor.fetchall():
                        data.append(dict(zip(columns, row)))
                    result["data"] = data
                    result["row_count"] = len(data)

                result["success"] = True

            except Exception as e:
                logger.error(f"PostgreSQL 执行失败: {e}")
                result["error"] = f"执行失败: {str(e)}"
            finally:
                if cursor:
                    cursor.close()
                connection.close()

        except Exception as e:
            logger.error(f"PostgreSQL 连接失败: {e}")
            result["error"] = f"连接失败: {str(e)}"

        return result


class SQLServerVerifierExecutor(BaseDBVerifierExecutor):
    """SQL Server 数据库验证和执行器"""

    def validate_sql(self, sql: str) -> Dict[str, Any]:
        """使用 SQL Server 验证 SQL 语句"""
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "validation_passed": False,
            "explain_result": None
        }

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

            cursor = None
            try:
                cursor = connection.cursor()
                clean_sql = sql.strip().rstrip(';')
                explain_sql = f"SET SHOWPLAN_XML ON; {clean_sql}; SET SHOWPLAN_XML OFF;"
                logger.info(f"执行执行计划: {explain_sql}")

                if "TOP" not in sql.upper() and "LIMIT" not in sql.upper():
                    if "ORDER BY" in sql.upper():
                        if clean_sql.upper().startswith("SELECT"):
                            modified_subquery = clean_sql[:6] + " TOP 100 PERCENT " + clean_sql[6:]
                        else:
                            modified_subquery = clean_sql
                        validation_sql = f"SELECT TOP 10 * FROM ({modified_subquery}) AS subq"
                    else:
                        validation_sql = f"SELECT TOP 10 * FROM ({clean_sql}) AS subq"
                else:
                    validation_sql = clean_sql
                cursor.execute(validation_sql)
                if cursor.description:
                    cursor.fetchall()

                result["validation_passed"] = True
                result["warnings"].append("SQL Server 验证通过")
                result["valid"] = True

            except Exception as e:
                logger.error(f"SQL Server 验证失败: {e}")
                result["errors"].append(f"验证失败: {str(e)}")
            finally:
                if cursor:
                    cursor.close()
                connection.close()

        except Exception as e:
            logger.error(f"SQL Server 连接失败: {e}")
            result["errors"].append(f"连接失败: {str(e)}")

        return result

    def execute_sql(self, sql: str) -> Dict[str, Any]:
        """使用 SQL Server 执行 SQL 语句"""
        result = {
            "success": False,
            "data": None,
            "columns": None,
            "row_count": 0,
            "error": None
        }

        try:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.config['host']},{self.config.get('port', 1433)};"
                f"DATABASE={self.config['database']};"
                f"UID={self.config['username']};"
                f"PWD={self.config['password']};"
                f"TrustServerCertificate=yes;"
            )
            connection = pyodbc.connect(conn_str, timeout=30)

            cursor = None
            try:
                cursor = connection.cursor()
                clean_sql = sql.strip().rstrip(';')

                if "TOP" not in sql.upper() and "LIMIT" not in sql.upper():
                    if "ORDER BY" in sql.upper():
                        execution_sql = clean_sql
                    else:
                        execution_sql = f"SELECT TOP 1000 * FROM ({clean_sql}) AS subq"
                else:
                    execution_sql = clean_sql

                logger.info(f"执行 SQL: {execution_sql}")
                cursor.execute(execution_sql)

                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    result["columns"] = columns

                if cursor.description:
                    data = []
                    columns = [desc[0] for desc in cursor.description]
                    for row in cursor.fetchall():
                        data.append(dict(zip(columns, row)))
                    result["data"] = data
                    result["row_count"] = len(data)

                result["success"] = True

            except Exception as e:
                logger.error(f"SQL Server 执行失败: {e}")
                result["error"] = f"执行失败: {str(e)}"
            finally:
                if cursor:
                    cursor.close()
                connection.close()

        except Exception as e:
            logger.error(f"SQL Server 连接失败: {e}")
            result["error"] = f"连接失败: {str(e)}"

        return result


class OracleVerifierExecutor(BaseDBVerifierExecutor):
    """Oracle 数据库验证和执行器"""
    
    _thick_mode_initialized = False

    @classmethod
    def _init_thick_mode(cls):
        """初始化 Oracle Thick 模式"""
        if cls._thick_mode_initialized:
            return
        
        try:
            oracle_client_lib_dir = os.getenv('ORACLE_CLIENT_LIB_DIR')
            if oracle_client_lib_dir:
                oracledb.init_oracle_client(lib_dir=oracle_client_lib_dir)
                logger.info("使用 Oracle Thick 模式连接")
            else:
                oracledb.init_oracle_client()
                logger.info("使用 Oracle Thick 模式连接（默认路径）")
            cls._thick_mode_initialized = True
        except Exception as init_error:
            logger.warning("无法初始化 Oracle 客户端，将使用 Thin 模式: %s", init_error)

    def validate_sql(self, sql: str) -> Dict[str, Any]:
        """使用 Oracle 验证 SQL 语句"""
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "validation_passed": False,
            "explain_result": None
        }

        try:
            self._init_thick_mode()
            dsn = self._build_dsn()
            connection = oracledb.connect(
                user=self.config['username'],
                password=self.config['password'],
                dsn=dsn
            )

            cursor = None
            try:
                cursor = connection.cursor()
                clean_sql = sql.strip().rstrip(';')
                explain_sql = f"EXPLAIN PLAN FOR {clean_sql}"
                logger.info(f"执行 EXPLAIN: {explain_sql}")
                cursor.execute(explain_sql)

                if "ROWNUM" not in sql.upper() and "FETCH" not in sql.upper():
                    validation_sql = f"SELECT * FROM ({clean_sql}) WHERE ROWNUM <= 10"
                else:
                    validation_sql = clean_sql
                cursor.execute(validation_sql)
                if cursor.description:
                    cursor.fetchall()

                result["validation_passed"] = True
                result["warnings"].append("Oracle 验证通过")
                result["valid"] = True

            except Exception as e:
                logger.error(f"Oracle 验证失败: {e}")
                result["errors"].append(f"验证失败: {str(e)}")
            finally:
                if cursor:
                    cursor.close()
                connection.close()

        except Exception as e:
            logger.error(f"Oracle 连接失败: {e}")
            result["errors"].append(f"连接失败: {str(e)}")

        return result

    def execute_sql(self, sql: str) -> Dict[str, Any]:
        """使用 Oracle 执行 SQL 语句"""
        result = {
            "success": False,
            "data": None,
            "columns": None,
            "row_count": 0,
            "error": None
        }

        try:
            self._init_thick_mode()
            dsn = self._build_dsn()
            connection = oracledb.connect(
                user=self.config['username'],
                password=self.config['password'],
                dsn=dsn
            )

            cursor = None
            try:
                cursor = connection.cursor()
                clean_sql = sql.strip().rstrip(';')

                if "ROWNUM" not in sql.upper() and "FETCH" not in sql.upper():
                    if "--" in sql:
                        execution_sql = clean_sql
                    else:
                        execution_sql = f"SELECT * FROM ({clean_sql}) WHERE ROWNUM <= 1000"
                else:
                    execution_sql = clean_sql

                logger.info(f"执行 SQL: {execution_sql}")
                cursor.execute(execution_sql)

                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    result["columns"] = columns

                if cursor.description:
                    data = []
                    columns = [desc[0] for desc in cursor.description]
                    for row in cursor.fetchall():
                        data.append(dict(zip(columns, row)))
                    result["data"] = data
                    result["row_count"] = len(data)

                result["success"] = True

            except Exception as e:
                logger.error(f"Oracle 执行失败: {e}")
                result["error"] = f"执行失败: {str(e)}"
            finally:
                if cursor:
                    cursor.close()
                connection.close()

        except Exception as e:
            logger.error(f"Oracle 连接失败: {e}")
            result["error"] = f"连接失败: {str(e)}"

        return result

    def _build_dsn(self):
        """构建 Oracle DSN"""
        host = self.config['host']
        port = int(self.config.get('port', 1521))
        mode = self.config.get('mode', 'service_name')
        db = self.config['database']

        if mode == 'service_name':
            return f"{host}:{port}/{db}"
        else:
            return f"{host}:{port}:{db}"


def get_db_verifier_executor(db_type: str, config: Dict[str, Any]) -> BaseDBVerifierExecutor:
    """
    获取数据库验证和执行器

    Args:
        db_type: 数据库类型
        config: 数据库配置

    Returns:
        对应的数据库验证和执行器实例
    """
    db_type = db_type.lower()

    if db_type == 'mysql':
        return MySQLVerifierExecutor(config)
    elif db_type in ['pg', 'postgresql']:
        return PostgreSQLVerifierExecutor(config)
    elif db_type in ['sqlserver', 'sql_server', 'mssql']:
        return SQLServerVerifierExecutor(config)
    elif db_type == 'oracle':
        return OracleVerifierExecutor(config)
    else:
        raise ValueError(f"不支持的数据库类型: {db_type}")
