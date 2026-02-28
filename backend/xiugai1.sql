-- 为t_datasource_field表添加索引相关字段
ALTER TABLE t_datasource_field
ADD COLUMN is_indexed BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否为索引字段',
ADD COLUMN index_name TEXT NULL COMMENT '索引名称',
ADD COLUMN index_type TEXT NULL COMMENT '索引类型: PRIMARY, UNIQUE, FULLTEXT, INDEX';