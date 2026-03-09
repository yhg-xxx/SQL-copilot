"""
历史查询示例检索器（升级为向量搜索版本）
使用 Chroma 向量数据库 + 阿里云 Embedding 进行语义相似度检索
"""

import logging
from typing import List, Dict, Any, Optional

from app.multi_agent.RAG.vector_store import get_vector_store

logger = logging.getLogger(__name__)


def retrieve_similar_history_examples(
    question: str,
    datasource_id: Optional[int] = None,
    user_id: Optional[int] = None,
    top_k: int = 3,
    max_history_days: int = 30
) -> List[Dict[str, Any]]:
    """
    检索相似的历史查询示例（基于向量相似度）

    Args:
        question: 当前用户问题
        datasource_id: 数据源ID（可选，用于过滤）
        user_id: 用户ID（可选，用于过滤）
        top_k: 返回的最大示例数量
        max_history_days: 检索最近多少天的历史（向量搜索已内置过滤，此参数保留兼容）

    Returns:
        历史示例列表，格式为 [{"question": "...", "sql": "...", "score": ..., "create_time": "..."}]
    """
    logger.info(f"开始检索历史查询示例（向量搜索），问题: {question}")

    if not question or not question.strip():
        return []

    try:
        vector_store = get_vector_store()

        examples = vector_store.search_similar_examples(
            question=question,
            datasource_id=datasource_id,
            user_id=user_id,
            top_k=top_k,
            score_threshold=0.5
        )

        formatted_examples = []
        for example in examples:
            formatted_examples.append({
                "question": example["question"],
                "sql": example["sql"],
                "create_time": example.get("create_time", ""),
                "score": example.get("score", 0.0)
            })

        logger.info(f"向量检索完成，返回 {len(formatted_examples)} 个相似示例")
        return formatted_examples

    except Exception as e:
        logger.error(f"向量检索历史查询示例失败: {e}", exc_info=True)
        logger.warning("回退到关键词匹配检索")
        return _fallback_keyword_search(question, datasource_id, user_id, top_k)


def _fallback_keyword_search(
    question: str,
    datasource_id: Optional[int] = None,
    user_id: Optional[int] = None,
    top_k: int = 3
) -> list[Any] | None:
    """
    回退方案：关键词匹配搜索（当向量搜索不可用时使用）
    """
    try:
        from app.database.db import SessionLocal
        from app.models.user_qa_record import UserQARecord

        db = SessionLocal()
        try:
            query = db.query(UserQARecord).filter(
                UserQARecord.generated_sql.isnot(None),
                UserQARecord.generated_sql != ""
            )

            if datasource_id:
                query = query.filter(UserQARecord.datasource_id == datasource_id)

            if user_id:
                query = query.filter(UserQARecord.user_id == user_id)

            history_records = query.order_by(
                UserQARecord.create_time.desc()
            ).limit(top_k * 3).all()

            if not history_records:
                return []

            examples = []
            for record in history_records:
                if record.question and record.generated_sql:
                    examples.append({
                        "question": record.question,
                        "sql": record.generated_sql,
                        "create_time": record.create_time.strftime("%Y-%m-%d %H:%M:%S") if record.create_time else "",
                        "score": 0.5
                    })

            return examples[:top_k]

        finally:
            db.close()

    except Exception as e:
        logger.error(f"关键词搜索也失败: {e}", exc_info=True)
        return []


def format_examples_for_prompt(examples: List[Dict[str, Any]]) -> str:
    """
    将检索到的示例格式化为提示词格式

    Args:
        examples: 历史示例列表

    Returns:
        格式化后的字符串
    """
    if not examples:
        return ""

    prompt_parts = ["===== 相似历史查询示例（基于语义相似度） ====="]

    for i, example in enumerate(examples, 1):
        score = example.get("score", 0)
        score_display = f" (相似度: {score:.2f})" if score > 0 else ""

        prompt_parts.append(f"\n示例 {i}{score_display}:")
        prompt_parts.append(f"用户问题: {example['question']}")
        prompt_parts.append(f"生成的SQL:")
        prompt_parts.append(f"```sql")
        prompt_parts.append(f"{example['sql']}")
        prompt_parts.append(f"```")

    prompt_parts.append("\n===========================================")

    return "\n".join(prompt_parts)


def save_query_to_vector_store(
    question: str,
    sql: str,
    datasource_id: Optional[int] = None,
    user_id: Optional[int] = None,
    record_id: Optional[int] = None
) -> bool:
    """
    保存新查询到向量数据库

    Args:
        question: 用户问题
        sql: 生成的SQL
        datasource_id: 数据源ID
        user_id: 用户ID
        record_id: 数据库记录ID

    Returns:
        是否保存成功
    """
    try:
        vector_store = get_vector_store()
        success = vector_store.add_query_example(
            question=question,
            sql=sql,
            datasource_id=datasource_id,
            user_id=user_id,
            record_id=record_id
        )
        return success
    except Exception as e:
        logger.error(f"保存查询到向量库失败: {e}", exc_info=True)
        return False
