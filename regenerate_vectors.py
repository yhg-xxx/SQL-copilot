#!/usr/bin/env python3
"""
重新生成指定数据源的表结构向量脚本

使用方法:
    python regenerate_vectors.py <datasource_id>

例如:
    python regenerate_vectors.py 22
"""

import sys
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 添加backend目录到Python路径
backend_dir = os.path.join(current_dir, 'backend')
sys.path.append(backend_dir)

from app.multi_agent.RAG.table_schema_retriever import save_datasource_tables_to_vector_store

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python regenerate_vectors.py <datasource_id>")
        print("例如: python regenerate_vectors.py 24")
        sys.exit(1)
    
    try:
        datasource_id = int(sys.argv[1])
    except ValueError:
        print("错误: 数据源ID必须是整数")
        sys.exit(1)
    
    print(f"开始重新生成数据源 {datasource_id} 的表结构向量...")
    
    try:
        success = save_datasource_tables_to_vector_store(datasource_id)
        if success:
            print(f"✅ 数据源 {datasource_id} 的表结构向量重新生成成功")
        else:
            print(f"❌ 数据源 {datasource_id} 的表结构向量重新生成失败")
    except Exception as e:
        print(f"❌ 重新生成表结构向量时发生错误: {str(e)}")
        logging.error(f"重新生成表结构向量失败: {e}", exc_info=True)

if __name__ == "__main__":
    main()
