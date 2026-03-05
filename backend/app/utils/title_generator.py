import logging
import re

logger = logging.getLogger(__name__)

def generate_conversation_title(content: str) -> str:
    """
    基于对话内容生成对话标题
    
    Args:
        content: 对话内容（通常是用户的第一个问题）
        
    Returns:
        生成的对话标题
    """
    try:
        # 检查内容是否为空
        if not content or len(content.strip()) == 0:
            return "新对话"
        
        # 去除首尾空格
        content = content.strip()
        
        # 移除标点符号
        content = re.sub(r'[，。！？；："\'（）【】{}、]', '', content)
        
        # 关键词提取
        keywords = extract_keywords(content)
        
        # 生成标题
        title = generate_title_from_keywords(keywords, content)
        
        # 确保标题长度不超过20个字符
        if len(title) > 20:
            title = title[:20]
        
        # 如果标题太短，补充相关内容
        if len(title) < 4:
            title = title + "查询"
        
        logger.info(f"生成的对话标题: {title}")
        return title
        
    except Exception as e:
        logger.error(f"生成对话标题失败: {e}")
        return "新对话"

def extract_keywords(content: str) -> list:
    """
    从内容中提取关键词
    
    Args:
        content: 对话内容
        
    Returns:
        关键词列表
    """
    # 常见的查询动词
    query_verbs = [
        "查询", "查找", "搜索", "获取", "得到", "显示", "列出",
        "统计", "计算", "汇总", "分析", "比较", "排序", "筛选",
        "更新", "修改", "删除", "添加", "插入", "创建"
    ]
    
    # 常见的业务术语
    business_terms = [
        "用户", "订单", "产品", "销售", "客户", "数据", "记录",
        "信息", "详情", "列表", "总数", "数量", "金额", "价格",
        "日期", "时间", "状态", "类型", "类别", "部门", "员工"
    ]
    
    keywords = []
    
    # 提取查询动词
    for verb in query_verbs:
        if verb in content:
            keywords.append(verb)
            break
    
    # 提取业务术语
    for term in business_terms:
        if term in content:
            keywords.append(term)
            if len(keywords) >= 3:
                break
    
    return keywords

def generate_title_from_keywords(keywords: list, original_content: str) -> str:
    """
    基于关键词生成标题
    
    Args:
        keywords: 关键词列表
        original_content: 原始内容
        
    Returns:
        生成的标题
    """
    if not keywords:
        # 如果没有提取到关键词，使用原始内容的前15个字符
        return original_content[:15]
    
    # 构建标题
    if len(keywords) == 1:
        # 只有一个关键词，添加"操作"
        return f"{keywords[0]}操作"
    elif len(keywords) == 2:
        # 两个关键词，组合成"动词+名词"
        return f"{keywords[0]}{keywords[1]}"
    else:
        # 三个或更多关键词，组合前三个
        return f"{keywords[0]}{keywords[1]}{keywords[2]}"

