import logging
from typing import Optional

from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = "sk-d1b70d8a21fc4337ae08674ee7608184"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"


def get_llm(temperature: float = 0.0, model_name: Optional[str] = None):
    """
    获取 DeepSeek 大模型实例
    
    Args:
        temperature: 温度参数
        model_name: 模型名称，默认使用 deepseek-chat
        
    Returns:
        ChatOpenAI 实例
    """
    model = model_name or DEEPSEEK_MODEL
    
    logger.info(f"初始化 DeepSeek 模型: {model}, temperature: {temperature}")
    
    return ChatOpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        model=model,
        temperature=temperature,
        max_tokens=4096
    )
