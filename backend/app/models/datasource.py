from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database.db import Base

class Datasource(Base):
    """数据源表"""
    __tablename__ = "t_datasource"
    __table_args__ = {"comment": "数据源表"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, comment="数据源名称")
    description = Column(Text, nullable=True, comment="描述")
    type = Column(Text, nullable=False, comment="数据源类型: mysql, postgresql, oracle, sqlserver等")
    type_name = Column(Text, nullable=True, comment="类型名称")
    configuration = Column(Text, nullable=False, comment="配置信息")
    created_at = Column(DateTime, nullable=True, server_default=func.now(), comment="创建时间")
    create_by = Column(Integer, nullable=True, comment="创建人ID")
    status = Column(Text, nullable=True, comment="状态: Success, Failed")
    num = Column(Text, nullable=True, comment="表数量统计: selected/total")
    table_relation = Column(JSON, nullable=True, comment="表关系")

class DatasourceTable(Base):
    """数据源表信息"""
    __tablename__ = "t_datasource_table"
    __table_args__ = {"comment": "数据源表信息"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ds_id = Column(Integer, ForeignKey("t_datasource.id", ondelete="CASCADE"), nullable=False, comment="数据源ID")
    checked = Column(Boolean, default=True, comment="是否选中")
    table_name = Column(Text, nullable=False, comment="表名")
    table_comment = Column(Text, nullable=True, comment="表注释")
    custom_comment = Column(Text, nullable=True, comment="自定义注释")
    embedding = Column(Text, nullable=True, comment="表结构 embedding (JSON 数组字符串)")

class DatasourceField(Base):
    """数据源字段信息"""
    __tablename__ = "t_datasource_field"
    __table_args__ = {"comment": "数据源字段信息"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ds_id = Column(Integer, ForeignKey("t_datasource.id", ondelete="CASCADE"), nullable=False, comment="数据源ID")
    table_id = Column(Integer, ForeignKey("t_datasource_table.id", ondelete="CASCADE"), nullable=False, comment="表ID")
    checked = Column(Boolean, default=True, comment="是否选中")
    field_name = Column(Text, nullable=False, comment="字段名")
    field_type = Column(Text, nullable=True, comment="字段类型")
    field_comment = Column(Text, nullable=True, comment="字段注释")
    custom_comment = Column(Text, nullable=True, comment="自定义注释")
    field_index = Column(Integer, nullable=True, comment="字段顺序")
    is_indexed = Column(Boolean, default=False, comment="是否为索引字段")
    index_name = Column(Text, nullable=True, comment="索引名称")
    index_type = Column(Text, nullable=True, comment="索引类型: PRIMARY, UNIQUE, FULLTEXT, INDEX")