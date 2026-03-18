import logging
from typing import Dict, Any, List, AsyncGenerator, Optional
from app.utils.llm_util import get_llm

logger = logging.getLogger(__name__)


async def stream_conversation_summary(
    chat_history: List[Dict[str, Any]],
    user_query: str = "生成对话总结",
    sql_execution_result: Optional[Dict[str, Any]] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    流式生成对话总结
    
    Args:
        chat_history: 对话历史
        user_query: 用户查询
        sql_execution_result: SQL执行结果
        
    Yields:
        流式输出的内容块
    """
    logger.info("[流式总结] 开始流式生成对话总结")
    
    if not chat_history and not sql_execution_result:
        yield {"type": "error", "content": "没有对话历史记录或查询结果"}
        return
    
    # 构建对话历史文本
    history_text = ""
    for idx, msg in enumerate(chat_history, 1):
        role = "用户" if msg.get("role") == "user" else "助手"
        content = msg.get("content", "")
        sql = msg.get("sql", "")
        
        history_text += f"\n{idx}. {role}: {content}"
        if sql:
            history_text += f"\n   SQL: {sql}"
    
    # 收集SQL结果数据
    sql_results_data = []
    if sql_execution_result:
        sql_results_data.append({
            "query": user_query,
            "columns": sql_execution_result.get("columns", []),
            "data": sql_execution_result.get("data", []),
            "row_count": sql_execution_result.get("row_count", 0)
        })
    
    # 构建提示词 - 简化版，用于流式输出
    prompt = f"""你是一个专业的数据分析助手。请分析以下 SQL 查询对话和查询结果，生成一份简洁的总结报告。

对话历史：
{history_text}

当前查询：{user_query}

SQL 执行结果数据：
{sql_results_data if sql_results_data else "无"}

请直接生成一份自然语言的总结报告，包含以下内容：

# 数据分析总结报告

## 1. 对话概述
简要描述这次对话的主要内容，包括用户的查询需求、查询的数据表、查询方式等。

## 2. 关键发现
- **发现 1**：列出主要的数据发现和洞察
- **发现 2**：基于查询结果的具体数据指标
- **发现 3**：数据模式、趋势或异常情况

## 3. SQL 查询分析
- **查询类型**：分析使用的 SQL 查询类型（如分组聚合、多表连接、条件筛选等）
- **查询目的**：说明查询的业务目的和价值

## 4. 建议
- **建议 1**：基于对话内容给出的第一条建议
- **建议 2**：基于对话内容给出的第二条建议
- **建议 3**：基于对话内容给出的第三条建议

**重要格式要求**：
1. 必须使用 `# ` 作为主标题（数据分析总结报告）
2. 必须使用 `## ` 作为四个主要章节的标题（对话概述、关键发现、SQL 查询分析、建议）
3. 不要使用 `###`、`####` 等更高级别的标题
4. 关键发现和建议部分使用 `- **关键词**：内容` 的格式
5. 用流畅的中文直接输出，不要使用 JSON 格式"""

    try:
        llm = get_llm()
        
        # 使用流式输出
        full_content = ""
        async for chunk in llm.astream(prompt):
            if hasattr(chunk, 'content') and chunk.content:
                content = chunk.content
                full_content += content
                yield {"type": "content", "content": content}
        
        # 如果有SQL执行结果，单独发送数据
        if sql_execution_result and sql_execution_result.get("data"):
            yield {
                "type": "data",
                "query_result_data": {
                    "columns": sql_execution_result.get("columns", []),
                    "data": sql_execution_result.get("data", []),
                    "row_count": sql_execution_result.get("row_count", 0)
                }
            }
        
        logger.info("[流式总结] 流式生成完成")
        
    except Exception as e:
        logger.error(f"[流式总结] 生成失败: {e}", exc_info=True)
        yield {"type": "error", "content": str(e)}

