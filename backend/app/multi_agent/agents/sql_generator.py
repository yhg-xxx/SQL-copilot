import logging
import json
from typing import Dict, List, Any

from langchain_core.messages import SystemMessage, HumanMessage

from app.multi_agent.state.agent_state import AgentState
from app.utils.llm_util import get_llm
from app.models.datasource import Datasource, DatasourceTable, DatasourceField

logger = logging.getLogger(__name__)


def get_datasource_schema(datasource_id: int) -> dict[Any, Any] | None:
    """
    获取数据源的表结构信息
    
    Args:
        datasource_id: 数据源ID
        
    Returns:
        包含表和字段信息的字典
    """
    try:
        from app.database.db import SessionLocal
        db = SessionLocal()
        
        try:
            # 获取数据源信息
            datasource = db.query(Datasource).filter(Datasource.id == datasource_id).first()
            if not datasource:
                logger.warning(f"未找到数据源: {datasource_id}")
                return {}
            
            # 获取表信息
            tables = db.query(DatasourceTable).filter(
                DatasourceTable.ds_id == datasource_id,
                DatasourceTable.checked == True
            ).all()
            
            schema = {}
            for table in tables:
                # 获取字段信息
                fields = db.query(DatasourceField).filter(
                    DatasourceField.table_id == table.id,
                    DatasourceField.checked == True
                ).order_by(DatasourceField.field_index).all()
                
                field_list = []
                for field in fields:
                    field_info = {
                        'name': field.field_name,
                        'type': field.field_type,
                        'comment': field.field_comment or field.custom_comment or '',
                        'is_indexed': field.is_indexed,
                        'index_name': field.index_name,
                        'index_type': field.index_type
                    }
                    field_list.append(field_info)
                
                schema[table.table_name] = {
                    'comment': table.table_comment or table.custom_comment or '',
                    'fields': field_list
                }
            
            logger.info(f"成功获取数据源 {datasource_id} 的表结构: {len(schema)} 张表")
            
            # 打印详细的表结构信息
            logger.info("=" * 80)
            logger.info("数据库表结构详情:")
            for table_name, table_info in schema.items():
                logger.info(f"\n表名: {table_name}")
                if table_info.get('comment'):
                    logger.info(f"  注释: {table_info['comment']}")
                logger.info(f"  字段数: {len(table_info.get('fields', []))}")
                for field in table_info.get('fields', []):
                    field_desc = f"    - {field['name']} ({field['type']})"
                    if field['comment']:
                        field_desc += f": {field['comment']}"
                    logger.info(field_desc)
            logger.info("=" * 80)
            
            return schema
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"获取数据源表结构失败: {e}", exc_info=True)
        return {}


def format_schema_for_prompt(schema: Dict[str, List[Dict]]) -> str:
    """
    将表结构格式化为适合 LLM 提示的文本
    
    Args:
        schema: 表结构字典
        
    Returns:
        格式化后的文本
    """
    if not schema:
        return "无可用表结构信息"
    
    lines = ["数据库表结构:"]
    for table_name, table_info in schema.items():
        lines.append(f"\n表名: {table_name}")
        if table_info.get('comment'):
            lines.append(f"  注释: {table_info['comment']}")
        lines.append("  字段:")
        for field in table_info.get('fields', []):
            field_desc = f"    - {field['name']} ({field['type']})"
            if field['comment']:
                field_desc += f": {field['comment']}"
            
            # 添加索引信息
            if field.get('is_indexed'):
                index_type = field.get('index_type') or 'INDEX'
                index_name = field.get('index_name') or 'unknown'
                field_desc += f" [{index_type} 索引: {index_name}]"
            
            lines.append(field_desc)
    
    return '\n'.join(lines)


def sql_generator(state: AgentState) -> AgentState:
    """
    SQL 生成智能体：负责根据用户查询生成 SQL 语句
    
    Args:
        state: 智能体状态
        
    Returns:
        更新后的状态
    """
    logger.info("SQL 生成智能体开始工作")
    
    try:
        user_query = state.get("user_query", "")
        datasource_id = state.get("datasource_id")
        
        if not user_query:
            state["error_message"] = "用户查询为空"
            return state
        
        # 获取数据源表结构
        schema = {}
        if datasource_id:
            schema = get_datasource_schema(datasource_id)
        
        # 格式化表结构信息
        schema_text = format_schema_for_prompt(schema)
        
        # 使用 DeepSeek 大模型生成 SQL
        system_prompt = f"""你是一个专业的 SQL 生成助手。请根据用户的自然语言查询和提供的数据库表结构，生成对应的 SQL 语句。

{schema_text}

请只返回 JSON 格式的结果，不要包含其他文字。
JSON 格式：
{{
  "success": true,
  "sql": "SELECT * FROM table_name",
  "message": ""
}}

注意事项：
1. 根据表结构和字段注释理解业务含义
2. 使用正确的表名和字段名
3. 考虑字段类型，避免类型错误
4. 如果查询条件需要，使用适当的 WHERE 子句
5. 如果需要连接多个表，使用适当的 JOIN 语句
6. 优先使用索引字段作为过滤条件、JOIN 条件和排序字段
7. 避免在非索引字段上进行大范围过滤或排序
8. 对于复杂查询，选择最优的执行计划"""
        
        user_prompt = f"用户查询: {user_query}"
        
        # 调用 LLM
        llm = get_llm(temperature=0.0)
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
            if result.get("success"):
                state["generated_sql"] = result.get("sql", "")
                logger.info(f"成功生成 SQL: {state['generated_sql']}")
            else:
                state["error_message"] = result.get("message", "SQL 生成失败")
        except json.JSONDecodeError:
            # 备用方案：直接返回简单 SQL
            if schema:
                table_name = list(schema.keys())[0]
                state["generated_sql"] = f"SELECT * FROM {table_name}; -- 查询: {user_query}"
            else:
                state["generated_sql"] = f"SELECT * FROM users; -- 查询: {user_query}"
            logger.info(f"使用备用 SQL 生成: {state['generated_sql']}")
        
    except Exception as e:
        logger.error(f"SQL 生成过程中发生错误: {e}", exc_info=True)
        state["error_message"] = f"SQL 生成失败: {str(e)}"
    
    return state
