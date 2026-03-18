import logging
import json
from typing import Any

from langchain_core.messages import SystemMessage, HumanMessage

from app.multi_agent.state.agent_state import AgentState
from app.utils.llm_util import get_llm
from app.models.datasource import Datasource, DatasourceTable
from app.database.db import SessionLocal

logger = logging.getLogger(__name__)

def get_datasource_info(datasource: Datasource) -> dict[str, str | list[Any] | int] | dict[
    str, str | list[Any] | int | Any] | None:
    """
    获取数据源的详细信息

    Args:
        datasource: 数据源对象

    Returns:
        包含数据源信息的字典
    """
    try:
        # 解析配置信息获取主机和数据库名
        host = ""
        database = ""
        try:
            config = json.loads(datasource.configuration)
            host = config.get("host", "")
            database = config.get("database", "")
        except Exception as e:
            logger.error(f"解析数据源配置失败: {e}")
        
        # 获取表信息
        tables_info = []
        try:
            db = SessionLocal()
            try:
                tables = db.query(DatasourceTable).filter(
                    DatasourceTable.ds_id == datasource.id,
                    DatasourceTable.checked == True
                ).limit(10).all()  # 只获取前10个表
                tables_info = [table.table_name for table in tables]
            finally:
                db.close()
        except Exception as e:
            logger.error(f"获取数据源表信息失败: {e}")
        
        return {
            "id": datasource.id,
            "name": datasource.name,
            "type": datasource.type,
            "host": host,
            "database": database,
            "tables": tables_info[:5]  # 只显示前5个表
        }
    except Exception as e:
        logger.error(f"获取数据源信息失败: {e}")
        return {
            "id": datasource.id,
            "name": datasource.name,
            "type": datasource.type,
            "host": "",
            "database": "",
            "tables": []
        }

def database_selector(state: AgentState) -> AgentState | None:
    """
    数据库选择智能体
    根据用户查询自动选择最合适的数据库
    
    Args:
        state: 智能体状态
        
    Returns:
        更新后的智能体状态
    """
    logger.info("数据库选择智能体启动")
    
    # 检查是否已经有数据源ID
    if state.get("datasource_id"):
        logger.info(f"已有数据源ID: {state['datasource_id']}，跳过数据库选择")
        return state
    
    user_query = state.get("user_query", "")
    user_id = state.get("user_id", 1)
    chat_history = state.get("chat_history", [])
    
    logger.info(f"用户查询: {user_query}")
    
    # 获取用户的所有数据源
    try:
        db = SessionLocal()
        try:
            datasources = db.query(Datasource).filter(
                Datasource.create_by == user_id
            ).all()
            logger.info(f"获取到 {len(datasources)} 个数据源")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"获取数据源失败: {e}")
        state["error_message"] = f"获取数据源失败: {str(e)}"
        return state
    
    if not datasources:
        logger.error("用户没有配置任何数据源")
        state["error_message"] = "用户没有配置任何数据源，请先添加数据源"
        return state
    
    # 如果只有一个数据源，直接选择
    if len(datasources) == 1:
        selected_datasource = datasources[0]
        logger.info(f"只有一个数据源，自动选择: {selected_datasource.name}")
        state["datasource_id"] = selected_datasource.id
        return state
    
    # 构建数据源信息
    datasource_info = []
    for ds in datasources:
        ds_info = get_datasource_info(ds)
        datasource_info.append(ds_info)
    
    # 格式化对话历史
    history_text = ""
    if chat_history:
        history_lines = []
        for i, item in enumerate(chat_history, 1):
            role = "用户" if item.get("role") == "user" else "助手"
            content = item.get("content", "").strip()
            history_lines.append(f"【第{i}轮】{role}: {content}")

        history_text = "\n".join(history_lines)
        history_text = f"""
===== 对话历史（共{len(chat_history)}轮） =====
{history_text}
====================================
"""
    
    # 格式化数据源信息
    formatted_datasource_info = "\n".join([
        f"ID: {ds['id']}, 名称: {ds['name']}, 类型: {ds['type']}, 主机: {ds['host']}, 数据库: {ds['database']}, 表: {', '.join(ds['tables'])}"
        for ds in datasource_info
    ])
    
    # 构建系统提示
    system_prompt = f"""你是一个数据库选择专家，需要根据用户的查询内容选择最合适的数据库。

用户查询: {user_query}

{history_text}

可用的数据源信息:
{formatted_datasource_info}

请分析用户查询的内容，考虑以下因素：
1. 查询中提到的表名或字段名
2. 查询的业务领域
3. 数据源的类型和名称
4. 对话历史中的上下文信息

请返回你认为最合适的数据源ID。
只返回数字ID，不要包含其他文字。"""
    
    # 构建用户提示
    user_prompt = f"用户查询: {user_query}"
    
    # 打印传递给大模型的完整信息
    logger.info("=" * 80)
    logger.info("传递给大模型的完整提示:")
    logger.info(f"系统提示（前500字符）: {system_prompt[:500]}...")
    logger.info(f"用户提示: {user_prompt}")
    logger.info("=" * 80)
    
    # 使用LLM选择数据库
    try:
        llm = get_llm(temperature=0.3)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        
        # 打印调用信息
        logger.info(f"调用大模型: {llm}, 消息长度: {len(messages)}")
        
        response = llm.invoke(messages)
        selected_id = response.content.strip()
        
        # 记录大模型原始响应
        logger.info("=" * 80)
        logger.info("大模型原始响应:")
        logger.info(selected_id)
        logger.info("=" * 80)
        
        # 验证返回的是否是有效的数字ID
        try:
            selected_id_int = int(selected_id)
            # 检查ID是否在可用数据源中
            valid_ids = [ds.id for ds in datasources]
            if selected_id_int not in valid_ids:
                logger.warning(f"模型返回的ID {selected_id_int} 不在可用数据源中，选择第一个数据源")
                selected_id_int = datasources[0].id
            
            selected_datasource = next((ds for ds in datasources if ds.id == selected_id_int), None)
            if selected_datasource:
                logger.info(f"智能体选择的数据源: {selected_datasource.name} (ID: {selected_id_int})")
                state["datasource_id"] = selected_id_int
            else:
                logger.warning("未找到匹配的数据源，选择第一个数据源")
                state["datasource_id"] = datasources[0].id
        except ValueError:
            logger.warning(f"模型返回的不是有效的数字ID: {selected_id}，选择第一个数据源")
            state["datasource_id"] = datasources[0].id
            
    except Exception as e:
        logger.error(f"数据库选择失败: {e}")
        # 失败时选择第一个数据源
        logger.info("数据库选择失败，选择第一个数据源")
        state["datasource_id"] = datasources[0].id
    
    logger.info("数据库选择智能体完成")
    return state