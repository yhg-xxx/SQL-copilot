-- ============================================
-- SQL Copilot 数据库迁移脚本
-- 添加 generated_sql 字段用于 RAG 检索
-- 日期: 2026-03-08
-- ============================================

-- 使用 sqlcopilot 数据库
USE sqlcopilot;

-- 添加 generated_sql 字段到 t_user_qa_record 表
-- 该字段用于存储原始生成的未优化SQL，专门用于 RAG 检索
ALTER TABLE t_user_qa_record 
ADD COLUMN generated_sql TEXT NULL COMMENT '原始生成的SQL（未优化，用于RAG检索）' 
AFTER datasource_id;

-- 同时更新 sql_statement 字段的注释，明确说明其用途
ALTER TABLE t_user_qa_record 
MODIFY COLUMN sql_statement TEXT NULL COMMENT '优化后的SQL（带注释，用于前端展示）';

-- 验证字段是否添加成功
SHOW COLUMNS FROM t_user_qa_record LIKE 'generated_sql';

-- 如果想回滚这个迁移，可以使用以下语句（注释掉）：
-- ALTER TABLE t_user_qa_record DROP COLUMN generated_sql;

-- ============================================
-- 迁移完成！
-- ============================================
