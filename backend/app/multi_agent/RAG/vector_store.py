"""
Chroma 向量数据库管理器
用于存储和检索历史查询示例的向量表示
"""

import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

import chromadb


from app.utils.embedding_util import  generate_embedding

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """
    Chroma 向量数据库管理类
    支持历史查询和表结构两个集合
    """

    def __init__(self, persist_directory: Optional[str] = None):
        """
        初始化 Chroma 向量数据库

        Args:
            persist_directory: 持久化目录，默认从环境变量读取或使用项目根目录下的 Chroma_db
        """
        if persist_directory is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            persist_directory = os.path.join(project_root, "Chroma_db")

        self.persist_directory = persist_directory
        os.makedirs(self.persist_directory, exist_ok=True)

        logger.info(f"初始化 Chroma 向量数据库，持久化目录: {self.persist_directory}")

        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # 历史查询集合
        self.history_collection_name = "history_queries"
        self.history_collection = self._get_or_create_collection(self.history_collection_name)
        
        # 表结构集合
        self.table_schema_collection_name = "table_schemas"
        self.table_schema_collection = self._get_or_create_collection(self.table_schema_collection_name)

        logger.info(f"Chroma 向量数据库初始化完成，集合: {self.history_collection_name}, {self.table_schema_collection_name}")

    def _get_or_create_collection(self, collection_name: str):
        """
        获取或创建指定名称的集合

        Args:
            collection_name: 集合名称

        Returns:
            Chroma 集合对象
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            logger.info(f"使用现有集合 {collection_name}，文档数量: {collection.count()}")
        except Exception:
            if collection_name == "history_queries":
                description = "历史查询示例集合"
            elif collection_name == "table_schemas":
                description = "表结构信息集合"
            else:
                description = "通用集合"
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": description}
            )
            logger.info(f"创建新集合: {collection_name}")
        return collection

    def add_query_example(
        self,
        question: str,
        sql: str,
        datasource_id: Optional[int] = None,
        user_id: Optional[int] = None,
        record_id: Optional[int] = None
    ) -> bool:
        """
        添加查询示例到向量数据库

        Args:
            question: 用户问题
            sql: 生成的SQL
            datasource_id: 数据源ID
            user_id: 用户ID
            record_id: 数据库记录ID

        Returns:
            是否添加成功
        """
        if not question or not sql:
            logger.warning("问题或SQL为空，跳过添加到向量库")
            return False

        try:
            embedding = generate_embedding(question)
            if embedding is None:
                logger.warning("生成 Embedding 失败，跳过添加到向量库")
                return False

            metadata = {
                "datasource_id": datasource_id or 0,
                "user_id": user_id or 0,
                "record_id": record_id or 0,
                "sql": sql,
                "create_time": datetime.now().isoformat()
            }

            doc_id = f"query_{record_id or int(datetime.now().timestamp() * 1000)}"

            self.history_collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[question],
                metadatas=[metadata]
            )

            logger.info(f"成功添加查询示例到向量库: {doc_id}")
            return True

        except Exception as e:
            logger.error(f"添加查询示例到向量库失败: {e}", exc_info=True)
            return False

    def add_table_schema(
        self,
        datasource_id: int,
        table_name: str,
        table_schema_text: str,
        table_comment: Optional[str] = None
    ) -> bool:
        """
        添加表结构到向量数据库

        Args:
            datasource_id: 数据源ID
            table_name: 表名
            table_schema_text: 表结构文本（包含字段信息）
            table_comment: 表注释

        Returns:
            是否添加成功
        """
        if not table_name or not table_schema_text:
            logger.warning("表名或表结构为空，跳过添加到向量库")
            return False

        try:
            embedding = generate_embedding(table_schema_text)
            if embedding is None:
                logger.warning(f"生成表 {table_name} Embedding 失败，跳过添加到向量库")
                return False

            metadata = {
                "datasource_id": datasource_id,
                "table_name": table_name,
                "table_comment": table_comment or "",
                "create_time": datetime.now().isoformat()
            }

            doc_id = f"table_{datasource_id}_{table_name}"

            self.table_schema_collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[table_schema_text],
                metadatas=[metadata]
            )

            logger.info(f"成功添加表结构到向量库: {doc_id}")
            return True

        except Exception as e:
            logger.error(f"添加表结构 {table_name} 到向量库失败: {e}", exc_info=True)
            return False

    def delete_datasource_tables(self, datasource_id: int) -> bool:
        """
        删除指定数据源的所有表结构

        Args:
            datasource_id: 数据源ID

        Returns:
            是否删除成功
        """
        try:
            where_clause = {"datasource_id": {"$eq": datasource_id}}
            self.table_schema_collection.delete(where=where_clause)
            logger.info(f"成功删除数据源 {datasource_id} 的所有表结构")
            return True
        except Exception as e:
            logger.error(f"删除数据源 {datasource_id} 表结构失败: {e}", exc_info=True)
            return False

    def search_similar_examples(
        self,
        question: str,
        datasource_id: Optional[int] = None,
        user_id: Optional[int] = None,
        top_k: int = 3,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        搜索相似的历史查询示例

        Args:
            question: 当前问题
            datasource_id: 数据源ID过滤（可选）
            user_id: 用户ID过滤（可选）
            top_k: 返回的最大数量
            score_threshold: 相似度阈值（0-1，越高越相似）

        Returns:
            相似示例列表，格式为 [{"question": "...", "sql": "...", "score": ...}]
        """
        if not question:
            return []

        try:
            logger.info(f"开始搜索相似示例，问题: {question[:50]}...")

            query_embedding = generate_embedding(question)
            if query_embedding is None:
                logger.warning("生成查询 Embedding 失败，返回空结果")
                return []

            where_clause = None
            if datasource_id and user_id:
                where_clause = {
                    "$and": [
                        {"datasource_id": {"$eq": datasource_id}},
                        {"user_id": {"$eq": user_id}}
                    ]
                }
            elif datasource_id:
                where_clause = {"datasource_id": {"$eq": datasource_id}}
            elif user_id:
                where_clause = {"user_id": {"$eq": user_id}}

            results = self.history_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k * 2,
                where=where_clause
            )

            examples = []
            if results and results.get("documents") and len(results["documents"]) > 0:
                for i, doc in enumerate(results["documents"][0]):
                    score = 1 - results["distances"][0][i] if results.get("distances") else 0.0

                    if score >= score_threshold:
                        metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                        examples.append({
                            "question": doc,
                            "sql": metadata.get("sql", ""),
                            "score": score,
                            "datasource_id": metadata.get("datasource_id"),
                            "user_id": metadata.get("user_id")
                        })

            examples = examples[:top_k]
            logger.info(f"搜索完成，找到 {len(examples)} 个相似示例")
            return examples

        except Exception as e:
            logger.error(f"搜索相似示例失败: {e}", exc_info=True)
            return []

    def search_relevant_tables(
        self,
        question: str,
        datasource_id: int,
        top_k: int = 10,
        score_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        搜索与用户问题相关的表结构

        Args:
            question: 用户问题
            datasource_id: 数据源ID
            top_k: 返回的最大表数量
            score_threshold: 相似度阈值

        Returns:
            相关表列表，格式为 [{"table_name": "...", "table_schema_text": "...", "score": ...}]
        """
        if not question or not datasource_id:
            return []

        try:
            logger.info(f"开始搜索相关表结构，问题: {question[:50]}...")

            query_embedding = generate_embedding(question)
            if query_embedding is None:
                logger.warning("生成查询 Embedding 失败，返回空结果")
                return []

            where_clause = {"datasource_id": {"$eq": datasource_id}}

            results = self.table_schema_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k * 2,
                where=where_clause
            )

            tables = []
            if results and results.get("documents") and len(results["documents"]) > 0:
                for i, doc in enumerate(results["documents"][0]):
                    score = 1 - results["distances"][0][i] if results.get("distances") else 0.0

                    if score >= score_threshold:
                        metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                        tables.append({
                            "table_name": metadata.get("table_name", ""),
                            "table_schema_text": doc,
                            "table_comment": metadata.get("table_comment", ""),
                            "score": score
                        })

            tables = tables[:top_k]
            logger.info(f"搜索完成，找到 {len(tables)} 个相关表")
            return tables

        except Exception as e:
            logger.error(f"搜索相关表失败: {e}", exc_info=True)
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        获取所有集合统计信息

        Returns:
            统计信息字典
        """
        try:
            history_count = self.history_collection.count()
            table_schema_count = self.table_schema_collection.count()
            return {
                "persist_directory": self.persist_directory,
                "collections": {
                    "history_queries": {
                        "document_count": history_count
                    },
                    "table_schemas": {
                        "document_count": table_schema_count
                    }
                }
            }
        except Exception as e:
            logger.error(f"获取集合统计失败: {e}")
            return {}

    def clear_collection(self, collection_name: Optional[str] = None):
        """
        清空指定集合或所有集合（慎用！）

        Args:
            collection_name: 集合名称，不传则清空所有集合
        """
        try:
            if collection_name:
                self.client.delete_collection(name=collection_name)
                if collection_name == self.history_collection_name:
                    self.history_collection = self._get_or_create_collection(collection_name)
                elif collection_name == self.table_schema_collection_name:
                    self.table_schema_collection = self._get_or_create_collection(collection_name)
                logger.warning(f"已清空集合: {collection_name}")
            else:
                self.client.delete_collection(name=self.history_collection_name)
                self.client.delete_collection(name=self.table_schema_collection_name)
                self.history_collection = self._get_or_create_collection(self.history_collection_name)
                self.table_schema_collection = self._get_or_create_collection(self.table_schema_collection_name)
                logger.warning("已清空所有集合")
        except Exception as e:
            logger.error(f"清空集合失败: {e}")


_vector_store_instance: Optional[ChromaVectorStore] = None


def get_vector_store() -> ChromaVectorStore:
    """
    获取向量存储单例

    Returns:
        ChromaVectorStore 实例
    """
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = ChromaVectorStore()
    return _vector_store_instance
