"""
共享工具函数模块
包含多个智能体共用的工具函数
"""

from typing import Dict, List


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
