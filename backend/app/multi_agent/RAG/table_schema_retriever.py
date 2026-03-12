"""
表结构 RAG 检索器
用于将表结构信息转换为向量并存储，以及根据用户问题检索相关表
"""

import logging
from typing import List, Dict, Any, Optional

from app.multi_agent.RAG.vector_store import get_vector_store
from app.models.datasource import DatasourceTable, DatasourceField
from app.database.db import SessionLocal

logger = logging.getLogger(__name__)


def format_table_schema_text(
    table_name: str,
    table_comment: Optional[str] = None,
    fields: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    将表结构格式化为适合向量化的文本

    Args:
        table_name: 表名
        table_comment: 表注释
        fields: 字段列表，每个字段包含 name, type, comment 等信息

    Returns:
        格式化后的表结构文本
    """
    lines = []
    lines.append(f"表名: {table_name}")

    if table_comment:
        lines.append(f"表注释: {table_comment}")

    if fields and len(fields) > 0:
        lines.append("字段信息:")
        for field in fields:
            field_desc = f"  - {field.get('name', '')} ({field.get('type', '')})"
            if field.get('comment'):
                field_desc += f": {field['comment']}"
            lines.append(field_desc)

    return "\n".join(lines)


def save_datasource_tables_to_vector_store(datasource_id: int) -> bool | None:
    """
    将数据源的所有表结构保存到向量数据库

    Args:
        datasource_id: 数据源ID

    Returns:
        是否保存成功
    """
    logger.info(f"开始保存数据源 {datasource_id} 的表结构到向量库")

    try:
        vector_store = get_vector_store()

        # 先删除该数据源已有的表结构
        vector_store.delete_datasource_tables(datasource_id)

        db = SessionLocal()
        try:
            # 获取所有已选中的表
            tables = db.query(DatasourceTable).filter(
                DatasourceTable.ds_id == datasource_id,
                DatasourceTable.checked == True
            ).all()

            success_count = 0
            for table in tables:
                # 获取该表的字段
                fields = db.query(DatasourceField).filter(
                    DatasourceField.table_id == table.id,
                    DatasourceField.checked == True
                ).order_by(DatasourceField.field_index).all()

                field_list = []
                for field in fields:
                    field_list.append({
                        "name": field.field_name,
                        "type": field.field_type,
                        "comment": field.field_comment or field.custom_comment or ""
                    })

                # 格式化表结构文本
                table_schema_text = format_table_schema_text(
                    table_name=table.table_name,
                    table_comment=table.table_comment or table.custom_comment or "",
                    fields=field_list
                )

                # 保存到向量库
                success = vector_store.add_table_schema(
                    datasource_id=datasource_id,
                    table_name=table.table_name,
                    table_schema_text=table_schema_text,
                    table_comment=table.table_comment or table.custom_comment or ""
                )

                if success:
                    success_count += 1

            logger.info(f"数据源 {datasource_id} 表结构保存完成，成功 {success_count}/{len(tables)} 个")
            return success_count > 0

        finally:
            db.close()

    except Exception as e:
        logger.error(f"保存数据源 {datasource_id} 表结构失败: {e}", exc_info=True)
        return False


def retrieve_relevant_tables(
    question: str,
    datasource_id: int,
    top_k: int = 20,  # 进一步增加返回的表数量
    score_threshold: float = 0.1  # 进一步降低相似度阈值，使检索更宽松
) -> List[Dict[str, Any]]:
    """
    根据用户问题检索相关的表结构

    Args:
        question: 用户问题
        datasource_id: 数据源ID
        top_k: 返回的最大表数量
        score_threshold: 相似度阈值

    Returns:
        相关表列表，格式为 [{"table_name": "...", "table_schema_text": "...", "score": ...}]
    """
    logger.info(f"开始检索相关表，问题: {question[:50]}...")

    try:
        vector_store = get_vector_store()

        tables = vector_store.search_relevant_tables(
            question=question,
            datasource_id=datasource_id,
            top_k=top_k,
            score_threshold=score_threshold
        )

        logger.info(f"检索完成，找到 {len(tables)} 个相关表")
        return tables

    except Exception as e:
        logger.error(f"检索相关表失败: {e}", exc_info=True)
        return []


def format_tables_for_prompt(tables: List[Dict[str, Any]]) -> str:
    """
    将检索到的表结构格式化为提示词格式

    Args:
        tables: 相关表列表

    Returns:
        格式化后的字符串
    """
    if not tables:
        return ""

    prompt_parts = ["===== 相关表结构（基于语义相似度检索） ====="]

    for i, table in enumerate(tables, 1):
        score = table.get("score", 0)
        score_display = f" (相似度: {score:.2f})" if score > 0 else ""

        prompt_parts.append(f"\n表 {i}{score_display}:")
        prompt_parts.append(table.get("table_schema_text", ""))

    prompt_parts.append("\n===========================================")

    return "\n".join(prompt_parts)
