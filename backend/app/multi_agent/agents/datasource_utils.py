import logging
import json
from typing import  Any
from app.database.db import SessionLocal
from app.models.datasource import Datasource

logger = logging.getLogger(__name__)


def get_datasource_config(datasource_id: int) -> dict[Any, Any] | None:
    """
    获取数据源的连接配置

    Args:
        datasource_id: 数据源ID

    Returns:
        连接配置字典，包含 db_type 字段
    """
    try:
        db = SessionLocal()

        try:
            datasource = db.query(Datasource).filter(Datasource.id == datasource_id).first()

            if not datasource:
                logger.warning(f"未找到数据源: {datasource_id}")
                return {}

            config = {}

            if hasattr(datasource, 'configuration') and datasource.configuration:
                try:
                    config_str = str(datasource.configuration)
                    logger.info(f"configuration 字段原始值: {config_str[:200]}")
                    if config_str:
                        config = json.loads(config_str)
                except json.JSONDecodeError as e:
                    logger.warning(f"解析 configuration 失败: {e}")
                except Exception as e:
                    logger.warning(f"处理 configuration 异常: {e}")

            if not config and hasattr(datasource, 'config') and datasource.config:
                try:
                    config_str = str(datasource.config)
                    logger.info(f"config 字段原始值: {config_str[:200]}")
                    if config_str:
                        config = json.loads(config_str)
                except (json.JSONDecodeError, AttributeError) as e:
                    logger.warning(f"解析 config 失败: {e}")

            if not config:
                for field in ['host', 'port', 'username', 'password', 'database']:
                    if hasattr(datasource, field):
                        value = getattr(datasource, field)
                        if value:
                            config[field] = value

            logger.info(f"解析后的配置字典: {config}")

            db_type = datasource.type if hasattr(datasource, 'type') else 'mysql'
            logger.info(f"数据源类型: {db_type}")

            default_port = 3306
            db_type_lower = db_type.lower()
            if db_type_lower in ['pg', 'postgresql']:
                default_port = 5432
            elif db_type_lower in ['sqlserver', 'sql_server', 'mssql']:
                default_port = 1433
            elif db_type_lower == 'oracle':
                default_port = 1521

            connection_config = {
                "db_type": db_type,
                "host": config.get("host"),
                "port": config.get("port", default_port),
                "username": config.get("username"),
                "password": config.get("password"),
                "database": config.get("database"),
                "db_schema": config.get("dbSchema", config.get("db_schema"))
            }

            required_fields = ["host", "username", "password", "database"]
            missing_fields = [field for field in required_fields if not connection_config.get(field)]

            if missing_fields:
                logger.warning(f"数据源 {datasource_id} 缺少必要字段: {missing_fields}")
                logger.warning(f"当前配置: {connection_config}")

            return connection_config

        finally:
            db.close()

    except Exception as e:
        logger.error(f"获取数据源配置失败: {e}", exc_info=True)
        return {}
