/*
 Navicat Premium Dump SQL

 Source Server         : localhost_3306_1
 Source Server Type    : MySQL
 Source Server Version : 80037 (8.0.37)
 Source Host           : localhost:3306
 Source Schema         : sqlcopilot

 Target Server Type    : MySQL
 Target Server Version : 80037 (8.0.37)
 File Encoding         : 65001

 Date: 14/03/2026 18:05:03
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for t_datasource
-- ----------------------------
DROP TABLE IF EXISTS `t_datasource`;
CREATE TABLE `t_datasource`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NOT NULL COMMENT '数据源名称',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NULL COMMENT '描述',
  `type` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NOT NULL COMMENT '数据源类型: mysql, postgresql, oracle, sqlserver等',
  `type_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NULL COMMENT '类型名称',
  `configuration` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NOT NULL COMMENT '配置信息(加密)',
  `create_by` int NULL DEFAULT NULL COMMENT '创建人ID',
  `status` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NULL COMMENT '状态: Success, Failed',
  `num` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NULL COMMENT '表数量统计: selected/total',
  `table_relation` json NULL COMMENT '表关系',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 42 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_as_ci COMMENT = '数据源表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for t_datasource_field
-- ----------------------------
DROP TABLE IF EXISTS `t_datasource_field`;
CREATE TABLE `t_datasource_field`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `ds_id` int NOT NULL COMMENT '数据源ID',
  `table_id` int NOT NULL COMMENT '表ID',
  `checked` tinyint(1) NULL DEFAULT NULL COMMENT '是否选中',
  `field_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NOT NULL COMMENT '字段名',
  `field_type` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NULL COMMENT '字段类型',
  `field_comment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NULL COMMENT '字段注释',
  `custom_comment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NULL COMMENT '自定义注释',
  `field_index` int NULL DEFAULT NULL COMMENT '字段顺序',
  `is_indexed` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否为索引字段',
  `index_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NULL COMMENT '索引名称',
  `index_type` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NULL COMMENT '索引类型: PRIMARY, UNIQUE, FULLTEXT, INDEX',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ds_id`(`ds_id` ASC) USING BTREE,
  INDEX `table_id`(`table_id` ASC) USING BTREE,
  CONSTRAINT `t_datasource_field_ibfk_1` FOREIGN KEY (`ds_id`) REFERENCES `t_datasource` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `t_datasource_field_ibfk_2` FOREIGN KEY (`table_id`) REFERENCES `t_datasource_table` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1057 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_as_ci COMMENT = '数据源字段信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for t_datasource_table
-- ----------------------------
DROP TABLE IF EXISTS `t_datasource_table`;
CREATE TABLE `t_datasource_table`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `ds_id` int NOT NULL COMMENT '数据源ID',
  `checked` tinyint(1) NULL DEFAULT NULL COMMENT '是否选中',
  `table_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NOT NULL COMMENT '表名',
  `table_comment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NULL COMMENT '表注释',
  `custom_comment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NULL COMMENT '自定义注释',
  `embedding` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NULL COMMENT '表结构 embedding (JSON 数组字符串)',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ds_id`(`ds_id` ASC) USING BTREE,
  CONSTRAINT `t_datasource_table_ibfk_1` FOREIGN KEY (`ds_id`) REFERENCES `t_datasource` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 134 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_as_ci COMMENT = '数据源表信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for t_user_conversation
-- ----------------------------
DROP TABLE IF EXISTS `t_user_conversation`;
CREATE TABLE `t_user_conversation`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `conversation_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '对话唯一标识',
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '对话标题',
  `last_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '最后一条消息',
  `last_message_time` datetime NULL DEFAULT NULL COMMENT '最后一条消息时间',
  `conversation_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'general' COMMENT '对话类型',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active' COMMENT '对话状态',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_conversation_id`(`conversation_id` ASC) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `fk_t_user_conversation_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 62 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用户对话表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for t_user_qa_record
-- ----------------------------
DROP TABLE IF EXISTS `t_user_qa_record`;
CREATE TABLE `t_user_qa_record`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` int NULL DEFAULT NULL COMMENT '用户ID',
  `uuid` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '自定义ID',
  `conversation_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '对话ID',
  `message_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '消息ID',
  `task_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '任务ID',
  `chat_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '对话ID',
  `question` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '用户问题',
  `to2_answer` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '大模型答案',
  `to4_answer` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '业务数据',
  `datasource_id` bigint NULL DEFAULT NULL COMMENT '数据源ID',
  `generated_sql` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '原始生成的SQL（未优化，用于RAG检索）',
  `sql_statement` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '优化后的SQL（带注释，用于前端展示）',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_conversation_id`(`conversation_id` ASC) USING BTREE,
  INDEX `idx_datasource_id`(`datasource_id` ASC) USING BTREE,
  INDEX `idx_create_time`(`create_time` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 124 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '问答记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NOT NULL COMMENT '用户名，唯一',
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NOT NULL COMMENT '密码哈希值',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_as_ci COMMENT = '用户表' ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
