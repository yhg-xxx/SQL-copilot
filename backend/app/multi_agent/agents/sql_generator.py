import logging
import json
from typing import  Any

from langchain_core.messages import SystemMessage, HumanMessage

from app.multi_agent.state.agent_state import AgentState
from app.utils.llm_util import get_llm
from app.models.datasource import Datasource, DatasourceTable, DatasourceField
from app.multi_agent.agents.schema_utils import format_schema_for_prompt
from app.multi_agent.RAG.history_retriever import retrieve_similar_history_examples, format_examples_for_prompt

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
                    # 添加索引信息
                    if field.get('is_indexed'):
                        index_type = field.get('index_type') or 'INDEX'
                        index_name = field.get('index_name') or 'unknown'
                        field_desc += f" [{index_type} 索引: {index_name}]"
                    logger.info(field_desc)
            logger.info("=" * 80)

            return schema

        finally:
            db.close()

    except Exception as e:
        logger.error(f"获取数据源表结构失败: {e}", exc_info=True)
        return {}


def sql_generator(state: AgentState) -> AgentState | None:
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
        user_id = state.get("user_id")
        chat_history = state.get("chat_history", [])

        if not user_query:
            state["error_message"] = "用户查询为空"
            return state

        # ========== RAG 历史查询检索 ==========
        logger.info("开始检索历史查询示例...")
        retrieved_examples = retrieve_similar_history_examples(
            question=user_query,
            datasource_id=datasource_id,
            user_id=user_id,
            top_k=3,
            max_history_days=30
        )
        state["retrieved_examples"] = retrieved_examples
        logger.info(f"检索到 {len(retrieved_examples)} 个历史示例")

        # 格式化历史示例为提示词
        examples_text = format_examples_for_prompt(retrieved_examples)
        if examples_text:
            logger.info("历史示例格式化为提示词成功")
        # ==========================================

        # 获取数据源表结构
        schema = {}
        db_type = "mysql"
        if datasource_id:
            schema = get_datasource_schema(datasource_id)
            # 获取数据库类型
            try:
                from app.database.db import SessionLocal
                from app.models.datasource import Datasource
                db = SessionLocal()
                try:
                    datasource = db.query(Datasource).filter(Datasource.id == datasource_id).first()
                    if datasource:
                        db_type = datasource.type if datasource.type else "mysql"
                        logger.info(f"数据源类型: {db_type}")
                finally:
                    db.close()
            except Exception as e:
                logger.warning(f"获取数据源类型失败: {e}")

        # 将表结构存入 state，供后续智能体使用
        state["db_info"] = schema
        state["db_type"] = db_type

        # 格式化表结构信息
        schema_text = format_schema_for_prompt(schema)

        # ========== 优化后的对话历史处理 ==========
        # 格式化对话历史 - 使用更清晰的时序标记
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

        # 打印历史记录到日志
        logger.info("=" * 80)
        logger.info("历史记录详情:")
        logger.info(f"用户查询: {user_query}")
        logger.info(f"数据源ID: {datasource_id}")
        logger.info(f"聊天历史长度: {len(chat_history)}")

        # 特别打印最近两轮的详细信息
        if len(chat_history) >= 2:
            logger.info("最近两轮对话详情:")
            for i in range(-2, 0):
                idx = len(chat_history) + i
                item = chat_history[idx]
                role = item.get("role", "unknown")
                content_preview = str(item.get("content", ""))[:200] + (
                    "..." if len(str(item.get("content", ""))) > 200 else "")
                logger.info(f"  第{idx + 1}轮 [{role}]: {content_preview}")

        for i, item in enumerate(chat_history):
            role = item.get("role", "unknown")
            content_preview = str(item.get("content", ""))[:200] + (
                "..." if len(str(item.get("content", ""))) > 200 else "")
            logger.info(f"历史记录 [{i}] - 角色: {role}, 内容预览: {content_preview}")
        logger.info("=" * 80)

        # 判断当前是否是修改请求
        is_modification = False
        last_sql_hint = ""

        if len(chat_history) >= 2:
            # 检查最后一条助手消息是否包含SQL
            for item in reversed(chat_history):
                if item.get("role") == "assistant":
                    assistant_content = item.get("content", "")
                    # 检查是否包含SQL关键词
                    sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "FROM", "WHERE",
                                    "JOIN"]
                    if any(keyword in assistant_content.upper() for keyword in sql_keywords):
                        is_modification = True
                        # 提取SQL相关部分
                        last_sql_hint = f"\n（提示：上一轮生成了SQL查询，当前可能是对该SQL的修改）"
                    break

        # 构建系统提示
        db_type_display = db_type
        if db_type.lower() == 'pg':
            db_type_display = 'PostgreSQL'
        elif db_type.lower() in ['sqlserver', 'sql_server', 'mssql']:
            db_type_display = 'SQL Server'
        
        system_prompt = f"""你是一个专业的 SQL 生成助手。请根据用户的自然语言查询、对话历史和提供的数据库表结构，生成对应的 SQL 语句。

重要：当前数据库类型是 {db_type_display}，请生成符合该数据库语法规范的 SQL 语句！

{schema_text}

{examples_text}

{history_text}

{'=' * 60}
重要：这是多轮对话的第{len(chat_history) + 1}轮
{'=' * 60}

核心指令：
1. 这是多轮对话，当前用户的查询是对话的延续
2. 请特别注意最近一轮（第{len(chat_history)}轮）的对话内容
3. 如果用户当前的查询涉及到修改、调整或优化，应该基于最近一轮助手的回答进行修改
4. 如果对话历史中有相关信息，请结合完整的对话历史来理解上下文
5. 如果当前查询明显是对上一轮SQL的修改，请基于上一轮的SQL进行调整

{'=' * 60}

当前查询：{user_query}
{last_sql_hint if is_modification else ''}

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
8. 对于复杂查询，选择最优的执行计划
9. 参考对话历史，理解用户的上下文需求
10. 确保生成的 SQL 符合 {db_type_display} 数据库的语法规范"""

        # 构建用户提示
        if is_modification and len(chat_history) > 0:
            user_prompt = f"用户查询: {user_query}\n\n（请注意：这是对上一轮对话结果的修改请求，请基于上一轮的回答进行调整）"
        else:
            user_prompt = f"用户查询: {user_query}"

        # 打印传递给大模型的完整信息
        logger.info("=" * 80)
        logger.info("传递给大模型的完整提示:")
        logger.info(f"系统提示（前500字符）: {system_prompt[:500]}...")
        logger.info(f"用户提示: {user_prompt}")
        logger.info("=" * 80)

        # 添加时序信息到日志
        if len(chat_history) > 0:
            logger.info(f"对话时序：当前是第{len(chat_history) + 1}轮，应该基于第{len(chat_history)}轮进行响应")
            if is_modification:
                logger.info("检测到当前查询可能是对上一轮SQL的修改")

        # 调用 LLM
        llm = get_llm(temperature=0.0)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        # 打印调用信息
        logger.info(f"调用大模型: {llm}, 消息长度: {len(messages)}")

        response = llm.invoke(messages)
        response_content = response.content.strip()

        # 记录大模型原始响应
        logger.info("=" * 80)
        logger.info("大模型原始响应:")
        logger.info(response_content[:500] + ("..." if len(response_content) > 500 else ""))
        logger.info("=" * 80)

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

                # 记录对话时序信息
                if is_modification:
                    logger.info("✅ 成功处理了修改请求")
            else:
                state["error_message"] = result.get("message", "SQL 生成失败")
        except json.JSONDecodeError as e:
            logger.error(f"解析大模型响应 JSON 失败: {e}")
            logger.error(f"清理后的响应内容: {response_content}")
            # 备用方案：直接返回简单 SQL
            if schema:
                table_name = list(schema.keys())[0]
                state["generated_sql"] = f"SELECT * FROM {table_name} LIMIT 10; -- 查询: {user_query}"
            else:
                state["generated_sql"] = f"SELECT * FROM users LIMIT 10; -- 查询: {user_query}"
            logger.info(f"使用备用 SQL 生成: {state['generated_sql']}")

    except Exception as e:
        logger.error(f"SQL 生成过程中发生错误: {e}", exc_info=True)
        state["error_message"] = f"SQL 生成失败: {str(e)}"

    return state