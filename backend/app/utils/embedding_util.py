"""
阿里云 Embedding 工具模块
使用阿里云 text-embedding-v4 模型生成文本向量
"""

import logging
import os
from typing import List, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class AliyunEmbedding:
    """
    阿里云 Embedding 客户端封装
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化阿里云 Embedding 客户端

        Args:
            api_key: 阿里云 API Key，默认从环境变量读取
            base_url: 阿里云 API Base URL，默认从环境变量读取
        """
        self.api_key = api_key or os.getenv("ALIYUN_EMBEDDING_API_KEY", "")
        self.base_url = base_url or os.getenv("ALIYUN_EMBEDDING_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.model = os.getenv("ALIYUN_EMBEDDING_MODEL", "text-embedding-v4")
        self.dimensions = int(os.getenv("ALIYUN_EMBEDDING_DIMENSIONS", "1024"))

        if not self.api_key:
            logger.warning("ALIYUN_EMBEDDING_API_KEY 未配置，Embedding 功能可能不可用")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        logger.info(f"阿里云 Embedding 客户端初始化完成，模型: {self.model}")

    def embed_query(self, text: str) -> Optional[List[float]]:
        """
        生成单个文本的向量表示

        Args:
            text: 输入文本

        Returns:
            向量列表，失败返回 None
        """
        if not text or not text.strip():
            return None

        try:
            logger.debug(f"正在生成文本 Embedding: {text[:50]}...")

            response = self.client.embeddings.create(
                model=self.model,
                input=text.strip(),
                dimensions=self.dimensions,
                encoding_format="float"
            )

            if response and response.data and len(response.data) > 0:
                embedding = response.data[0].embedding
                logger.debug(f"Embedding 生成成功，维度: {len(embedding)}")
                return embedding
            else:
                logger.warning("Embedding API 返回空结果")
                return None

        except Exception as e:
            logger.error(f"生成 Embedding 失败: {e}", exc_info=True)
            return None

    def embed_documents(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        批量生成文本向量

        Args:
            texts: 文本列表

        Returns:
            向量列表，顺序与输入一致，失败项为 None
        """
        results = []
        for text in texts:
            embedding = self.embed_query(text)
            results.append(embedding)
        return results


# 全局单例
_embedding_instance: Optional[AliyunEmbedding] = None


def get_embedding_client() -> AliyunEmbedding:
    """
    获取 Embedding 客户端单例

    Returns:
        AliyunEmbedding 实例
    """
    global _embedding_instance
    if _embedding_instance is None:
        _embedding_instance = AliyunEmbedding()
    return _embedding_instance


def generate_embedding(text: str) -> Optional[List[float]]:
    """
    便捷函数：生成单个文本的向量

    Args:
        text: 输入文本

    Returns:
        向量列表
    """
    client = get_embedding_client()
    return client.embed_query(text)
