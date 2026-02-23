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

 Date: 23/02/2026 22:16:08
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
  `create_time` datetime NULL DEFAULT (now()) COMMENT '创建时间',
  `create_by` int NULL DEFAULT NULL COMMENT '创建人ID',
  `status` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NULL COMMENT '状态: Success, Failed',
  `num` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci NULL COMMENT '表数量统计: selected/total',
  `table_relation` json NULL COMMENT '表关系',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 22 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_as_ci COMMENT = '数据源表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_datasource
-- ----------------------------
INSERT INTO `t_datasource` VALUES (1, 'chi1', '测试', 'mysql', 'MySQL', '{\"host\": \"localhost\", \"port\": \"3306\", \"database\": \"chi\", \"username\": \"root\", \"password\": \"123456\"}', '2026-02-12 09:34:08', 1, 'Success', '2/2', NULL);
INSERT INTO `t_datasource` VALUES (4, '1', '1', 'postgresql', 'PostgreSQL', '{\"host\": \"1\", \"port\": \"1\", \"database\": \"1\", \"username\": \"1\", \"password\": \"1\"}', '2026-02-20 21:51:08', 1, 'Success', '0/0', NULL);
INSERT INTO `t_datasource` VALUES (5, '2', '2', 'mysql', 'MySQL', '{\"host\": \"2\", \"port\": \"2\", \"database\": \"2\", \"username\": \"2\", \"password\": \"2\"}', '2026-02-20 21:52:02', 1, 'Failed', '0/0', NULL);
INSERT INTO `t_datasource` VALUES (21, '4', '4', 'mysql', 'MySQL', '{\"host\": \"localhost\", \"port\": \"3306\", \"database\": \"parts\", \"username\": \"root\", \"password\": \"123456\"}', '2026-02-21 21:32:39', 1, 'Success', '13/13', '\"{\\\"cells\\\": [{\\\"position\\\": {\\\"x\\\": -20, \\\"y\\\": -140}, \\\"size\\\": {\\\"width\\\": 200, \\\"height\\\": 591}, \\\"attrs\\\": {\\\"text\\\": {\\\"text\\\": \\\"fault_order\\\"}}, \\\"visible\\\": true, \\\"shape\\\": \\\"er-rect\\\", \\\"ports\\\": {\\\"groups\\\": {\\\"list\\\": {\\\"markup\\\": [{\\\"tagName\\\": \\\"rect\\\", \\\"selector\\\": \\\"portBody\\\"}, {\\\"tagName\\\": \\\"text\\\", \\\"selector\\\": \\\"portNameLabel\\\"}], \\\"attrs\\\": {\\\"portBody\\\": {\\\"width\\\": 200, \\\"height\\\": 36, \\\"stroke\\\": \\\"#DEE0E3\\\", \\\"strokeWidth\\\": 0.5, \\\"fill\\\": \\\"#ffffff\\\", \\\"magnet\\\": true}, \\\"portNameLabel\\\": {\\\"ref\\\": \\\"portBody\\\", \\\"refX\\\": 12, \\\"refY\\\": 9.5, \\\"fontSize\\\": 13, \\\"fontWeight\\\": 500, \\\"textAnchor\\\": \\\"left\\\", \\\"fill\\\": \\\"#1F2329\\\", \\\"textWrap\\\": {\\\"width\\\": 120, \\\"height\\\": 20, \\\"ellipsis\\\": true}}}, \\\"position\\\": \\\"erPortPosition\\\"}}, \\\"items\\\": [{\\\"id\\\": \\\"port-28-254\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"fault_id\\\"}}}, {\\\"id\\\": \\\"port-28-255\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"part_id\\\"}}}, {\\\"id\\\": \\\"port-28-256\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"sn\\\"}}}, {\\\"id\\\": \\\"port-28-257\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"fault_time\\\"}}}, {\\\"id\\\": \\\"port-28-258\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"reported_by\\\"}}}, {\\\"id\\\": \\\"port-28-259\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"fault_description\\\"}}}, {\\\"id\\\": \\\"port-28-260\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"work_order_status\\\"}}}, {\\\"id\\\": \\\"port-28-261\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"repair_result\\\"}}}, {\\\"id\\\": \\\"port-28-262\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"repair_by\\\"}}}, {\\\"id\\\": \\\"port-28-263\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"processed_at\\\"}}}, {\\\"id\\\": \\\"port-28-264\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"review_result\\\"}}}, {\\\"id\\\": \\\"port-28-265\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"review_by\\\"}}}, {\\\"id\\\": \\\"port-28-266\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"review_at\\\"}}}, {\\\"id\\\": \\\"port-28-267\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"disposal_type\\\"}}}, {\\\"id\\\": \\\"port-28-268\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"created_at\\\"}}}]}, \\\"id\\\": \\\"node-28\\\", \\\"zIndex\\\": 1}, {\\\"position\\\": {\\\"x\\\": 300, \\\"y\\\": 50}, \\\"size\\\": {\\\"width\\\": 200, \\\"height\\\": 663}, \\\"attrs\\\": {\\\"text\\\": {\\\"text\\\": \\\"inbound_record\\\"}}, \\\"visible\\\": true, \\\"shape\\\": \\\"er-rect\\\", \\\"ports\\\": {\\\"groups\\\": {\\\"list\\\": {\\\"markup\\\": [{\\\"tagName\\\": \\\"rect\\\", \\\"selector\\\": \\\"portBody\\\"}, {\\\"tagName\\\": \\\"text\\\", \\\"selector\\\": \\\"portNameLabel\\\"}], \\\"attrs\\\": {\\\"portBody\\\": {\\\"width\\\": 200, \\\"height\\\": 36, \\\"stroke\\\": \\\"#DEE0E3\\\", \\\"strokeWidth\\\": 0.5, \\\"fill\\\": \\\"#ffffff\\\", \\\"magnet\\\": true}, \\\"portNameLabel\\\": {\\\"ref\\\": \\\"portBody\\\", \\\"refX\\\": 12, \\\"refY\\\": 9.5, \\\"fontSize\\\": 13, \\\"fontWeight\\\": 500, \\\"textAnchor\\\": \\\"left\\\", \\\"fill\\\": \\\"#1F2329\\\", \\\"textWrap\\\": {\\\"width\\\": 120, \\\"height\\\": 20, \\\"ellipsis\\\": true}}}, \\\"position\\\": \\\"erPortPosition\\\"}}, \\\"items\\\": [{\\\"id\\\": \\\"port-29-269\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"inbound_id\\\"}}}, {\\\"id\\\": \\\"port-29-270\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"order_id\\\"}}}, {\\\"id\\\": \\\"port-29-271\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"location_id\\\"}}}, {\\\"id\\\": \\\"port-29-272\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"spare_part_category\\\"}}}, {\\\"id\\\": \\\"port-29-273\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"spare_part_status\\\"}}}, {\\\"id\\\": \\\"port-29-274\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"spare_part_type\\\"}}}, {\\\"id\\\": \\\"port-29-275\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"unit_price\\\"}}}, {\\\"id\\\": \\\"port-29-276\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"tax_rate\\\"}}}, {\\\"id\\\": \\\"port-29-277\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"tax_free_unit_price\\\"}}}, {\\\"id\\\": \\\"port-29-278\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"tax_amount\\\"}}}, {\\\"id\\\": \\\"port-29-279\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"tax_free_total\\\"}}}, {\\\"id\\\": \\\"port-29-280\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"total_tax\\\"}}}, {\\\"id\\\": \\\"port-29-281\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"sn\\\"}}}, {\\\"id\\\": \\\"port-29-282\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"unit\\\"}}}, {\\\"id\\\": \\\"port-29-283\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"manufacturer\\\"}}}, {\\\"id\\\": \\\"port-29-284\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"warranty_until\\\"}}}, {\\\"id\\\": \\\"port-29-285\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"created_at\\\"}}}]}, \\\"id\\\": \\\"node-29\\\", \\\"zIndex\\\": 1}, {\\\"position\\\": {\\\"x\\\": 550, \\\"y\\\": 50}, \\\"size\\\": {\\\"width\\\": 200, \\\"height\\\": 267}, \\\"attrs\\\": {\\\"text\\\": {\\\"text\\\": \\\"inventory\\\"}}, \\\"visible\\\": true, \\\"shape\\\": \\\"er-rect\\\", \\\"ports\\\": {\\\"groups\\\": {\\\"list\\\": {\\\"markup\\\": [{\\\"tagName\\\": \\\"rect\\\", \\\"selector\\\": \\\"portBody\\\"}, {\\\"tagName\\\": \\\"text\\\", \\\"selector\\\": \\\"portNameLabel\\\"}], \\\"attrs\\\": {\\\"portBody\\\": {\\\"width\\\": 200, \\\"height\\\": 36, \\\"stroke\\\": \\\"#DEE0E3\\\", \\\"strokeWidth\\\": 0.5, \\\"fill\\\": \\\"#ffffff\\\", \\\"magnet\\\": true}, \\\"portNameLabel\\\": {\\\"ref\\\": \\\"portBody\\\", \\\"refX\\\": 12, \\\"refY\\\": 9.5, \\\"fontSize\\\": 13, \\\"fontWeight\\\": 500, \\\"textAnchor\\\": \\\"left\\\", \\\"fill\\\": \\\"#1F2329\\\", \\\"textWrap\\\": {\\\"width\\\": 120, \\\"height\\\": 20, \\\"ellipsis\\\": true}}}, \\\"position\\\": \\\"erPortPosition\\\"}}, \\\"items\\\": [{\\\"id\\\": \\\"port-30-286\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"inventory_id\\\"}}}, {\\\"id\\\": \\\"port-30-287\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"part_name\\\"}}}, {\\\"id\\\": \\\"port-30-288\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"location_name\\\"}}}, {\\\"id\\\": \\\"port-30-289\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"status\\\"}}}, {\\\"id\\\": \\\"port-30-290\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"number\\\"}}}, {\\\"id\\\": \\\"port-30-291\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"safety_stock\\\"}}}]}, \\\"id\\\": \\\"node-30\\\", \\\"zIndex\\\": 1}, {\\\"position\\\": {\\\"x\\\": -240, \\\"y\\\": 310}, \\\"size\\\": {\\\"width\\\": 200, \\\"height\\\": 411}, \\\"attrs\\\": {\\\"text\\\": {\\\"text\\\": \\\"purchase_order\\\"}}, \\\"visible\\\": true, \\\"shape\\\": \\\"er-rect\\\", \\\"ports\\\": {\\\"groups\\\": {\\\"list\\\": {\\\"markup\\\": [{\\\"tagName\\\": \\\"rect\\\", \\\"selector\\\": \\\"portBody\\\"}, {\\\"tagName\\\": \\\"text\\\", \\\"selector\\\": \\\"portNameLabel\\\"}], \\\"attrs\\\": {\\\"portBody\\\": {\\\"width\\\": 200, \\\"height\\\": 36, \\\"stroke\\\": \\\"#DEE0E3\\\", \\\"strokeWidth\\\": 0.5, \\\"fill\\\": \\\"#ffffff\\\", \\\"magnet\\\": true}, \\\"portNameLabel\\\": {\\\"ref\\\": \\\"portBody\\\", \\\"refX\\\": 12, \\\"refY\\\": 9.5, \\\"fontSize\\\": 13, \\\"fontWeight\\\": 500, \\\"textAnchor\\\": \\\"left\\\", \\\"fill\\\": \\\"#1F2329\\\", \\\"textWrap\\\": {\\\"width\\\": 120, \\\"height\\\": 20, \\\"ellipsis\\\": true}}}, \\\"position\\\": \\\"erPortPosition\\\"}}, \\\"items\\\": [{\\\"id\\\": \\\"port-31-292\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"order_id\\\"}}}, {\\\"id\\\": \\\"port-31-293\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"applicant_id\\\"}}}, {\\\"id\\\": \\\"port-31-294\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"station\\\"}}}, {\\\"id\\\": \\\"port-31-295\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"workshop\\\"}}}, {\\\"id\\\": \\\"port-31-296\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"status\\\"}}}, {\\\"id\\\": \\\"port-31-297\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"spare_part_name\\\"}}}, {\\\"id\\\": \\\"port-31-298\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"spare_part_model\\\"}}}, {\\\"id\\\": \\\"port-31-299\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"number\\\"}}}, {\\\"id\\\": \\\"port-31-300\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"created_at\\\"}}}, {\\\"id\\\": \\\"port-31-301\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"completed_at\\\"}}}]}, \\\"id\\\": \\\"node-31\\\", \\\"zIndex\\\": 1}, {\\\"position\\\": {\\\"x\\\": 300, \\\"y\\\": 350}, \\\"size\\\": {\\\"width\\\": 200, \\\"height\\\": 231}, \\\"attrs\\\": {\\\"text\\\": {\\\"text\\\": \\\"purchase_order_status_history\\\"}}, \\\"visible\\\": true, \\\"shape\\\": \\\"er-rect\\\", \\\"ports\\\": {\\\"groups\\\": {\\\"list\\\": {\\\"markup\\\": [{\\\"tagName\\\": \\\"rect\\\", \\\"selector\\\": \\\"portBody\\\"}, {\\\"tagName\\\": \\\"text\\\", \\\"selector\\\": \\\"portNameLabel\\\"}], \\\"attrs\\\": {\\\"portBody\\\": {\\\"width\\\": 200, \\\"height\\\": 36, \\\"stroke\\\": \\\"#DEE0E3\\\", \\\"strokeWidth\\\": 0.5, \\\"fill\\\": \\\"#ffffff\\\", \\\"magnet\\\": true}, \\\"portNameLabel\\\": {\\\"ref\\\": \\\"portBody\\\", \\\"refX\\\": 12, \\\"refY\\\": 9.5, \\\"fontSize\\\": 13, \\\"fontWeight\\\": 500, \\\"textAnchor\\\": \\\"left\\\", \\\"fill\\\": \\\"#1F2329\\\", \\\"textWrap\\\": {\\\"width\\\": 120, \\\"height\\\": 20, \\\"ellipsis\\\": true}}}, \\\"position\\\": \\\"erPortPosition\\\"}}, \\\"items\\\": [{\\\"id\\\": \\\"port-32-302\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"history_id\\\"}}}, {\\\"id\\\": \\\"port-32-303\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"order_id\\\"}}}, {\\\"id\\\": \\\"port-32-304\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"status\\\"}}}, {\\\"id\\\": \\\"port-32-305\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"changed_by\\\"}}}, {\\\"id\\\": \\\"port-32-306\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"changed_at\\\"}}}]}, \\\"id\\\": \\\"node-32\\\", \\\"zIndex\\\": 1}, {\\\"position\\\": {\\\"x\\\": 550, \\\"y\\\": 350}, \\\"size\\\": {\\\"width\\\": 200, \\\"height\\\": 663}, \\\"attrs\\\": {\\\"text\\\": {\\\"text\\\": \\\"return_factory_record\\\"}}, \\\"visible\\\": true, \\\"shape\\\": \\\"er-rect\\\", \\\"ports\\\": {\\\"groups\\\": {\\\"list\\\": {\\\"markup\\\": [{\\\"tagName\\\": \\\"rect\\\", \\\"selector\\\": \\\"portBody\\\"}, {\\\"tagName\\\": \\\"text\\\", \\\"selector\\\": \\\"portNameLabel\\\"}], \\\"attrs\\\": {\\\"portBody\\\": {\\\"width\\\": 200, \\\"height\\\": 36, \\\"stroke\\\": \\\"#DEE0E3\\\", \\\"strokeWidth\\\": 0.5, \\\"fill\\\": \\\"#ffffff\\\", \\\"magnet\\\": true}, \\\"portNameLabel\\\": {\\\"ref\\\": \\\"portBody\\\", \\\"refX\\\": 12, \\\"refY\\\": 9.5, \\\"fontSize\\\": 13, \\\"fontWeight\\\": 500, \\\"textAnchor\\\": \\\"left\\\", \\\"fill\\\": \\\"#1F2329\\\", \\\"textWrap\\\": {\\\"width\\\": 120, \\\"height\\\": 20, \\\"ellipsis\\\": true}}}, \\\"position\\\": \\\"erPortPosition\\\"}}, \\\"items\\\": [{\\\"id\\\": \\\"port-33-307\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"return_id\\\"}}}, {\\\"id\\\": \\\"port-33-308\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"actual_return_time\\\"}}}, {\\\"id\\\": \\\"port-33-309\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"created_at\\\"}}}, {\\\"id\\\": \\\"port-33-310\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"created_by\\\"}}}, {\\\"id\\\": \\\"port-33-311\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"expected_repair_days\\\"}}}, {\\\"id\\\": \\\"port-33-312\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"expected_return_time\\\"}}}, {\\\"id\\\": \\\"port-33-313\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"fault_id\\\"}}}, {\\\"id\\\": \\\"port-33-314\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"logistics_company\\\"}}}, {\\\"id\\\": \\\"port-33-315\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"logistics_number\\\"}}}, {\\\"id\\\": \\\"port-33-316\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"part_id\\\"}}}, {\\\"id\\\": \\\"port-33-317\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"repair_description\\\"}}}, {\\\"id\\\": \\\"port-33-318\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"repair_result\\\"}}}, {\\\"id\\\": \\\"port-33-319\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"return_reason\\\"}}}, {\\\"id\\\": \\\"port-33-320\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"sent_time\\\"}}}, {\\\"id\\\": \\\"port-33-321\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"sn\\\"}}}, {\\\"id\\\": \\\"port-33-322\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"status\\\"}}}, {\\\"id\\\": \\\"port-33-323\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"updated_at\\\"}}}]}, \\\"id\\\": \\\"node-33\\\", \\\"zIndex\\\": 1}, {\\\"position\\\": {\\\"x\\\": -560, \\\"y\\\": 330}, \\\"size\\\": {\\\"width\\\": 200, \\\"height\\\": 411}, \\\"attrs\\\": {\\\"text\\\": {\\\"text\\\": \\\"scrap_records\\\"}}, \\\"visible\\\": true, \\\"shape\\\": \\\"er-rect\\\", \\\"ports\\\": {\\\"groups\\\": {\\\"list\\\": {\\\"markup\\\": [{\\\"tagName\\\": \\\"rect\\\", \\\"selector\\\": \\\"portBody\\\"}, {\\\"tagName\\\": \\\"text\\\", \\\"selector\\\": \\\"portNameLabel\\\"}], \\\"attrs\\\": {\\\"portBody\\\": {\\\"width\\\": 200, \\\"height\\\": 36, \\\"stroke\\\": \\\"#DEE0E3\\\", \\\"strokeWidth\\\": 0.5, \\\"fill\\\": \\\"#ffffff\\\", \\\"magnet\\\": true}, \\\"portNameLabel\\\": {\\\"ref\\\": \\\"portBody\\\", \\\"refX\\\": 12, \\\"refY\\\": 9.5, \\\"fontSize\\\": 13, \\\"fontWeight\\\": 500, \\\"textAnchor\\\": \\\"left\\\", \\\"fill\\\": \\\"#1F2329\\\", \\\"textWrap\\\": {\\\"width\\\": 120, \\\"height\\\": 20, \\\"ellipsis\\\": true}}}, \\\"position\\\": \\\"erPortPosition\\\"}}, \\\"items\\\": [{\\\"id\\\": \\\"port-34-324\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"order_id\\\"}}}, {\\\"id\\\": \\\"port-34-325\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"applicant_id\\\"}}}, {\\\"id\\\": \\\"port-34-326\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"apply_time\\\"}}}, {\\\"id\\\": \\\"port-34-327\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"damage_photo\\\"}}}, {\\\"id\\\": \\\"port-34-328\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"disposal_method\\\"}}}, {\\\"id\\\": \\\"port-34-329\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"executor\\\"}}}, {\\\"id\\\": \\\"port-34-330\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"part_status\\\"}}}, {\\\"id\\\": \\\"port-34-331\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"scrap_reason\\\"}}}, {\\\"id\\\": \\\"port-34-332\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"scrap_time\\\"}}}, {\\\"id\\\": \\\"port-34-333\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"sn\\\"}}}]}, \\\"id\\\": \\\"node-34\\\", \\\"zIndex\\\": 1}, {\\\"position\\\": {\\\"x\\\": 300, \\\"y\\\": 650}, \\\"size\\\": {\\\"width\\\": 200, \\\"height\\\": 447}, \\\"attrs\\\": {\\\"text\\\": {\\\"text\\\": \\\"spare_part\\\"}}, \\\"visible\\\": true, \\\"shape\\\": \\\"er-rect\\\", \\\"ports\\\": {\\\"groups\\\": {\\\"list\\\": {\\\"markup\\\": [{\\\"tagName\\\": \\\"rect\\\", \\\"selector\\\": \\\"portBody\\\"}, {\\\"tagName\\\": \\\"text\\\", \\\"selector\\\": \\\"portNameLabel\\\"}], \\\"attrs\\\": {\\\"portBody\\\": {\\\"width\\\": 200, \\\"height\\\": 36, \\\"stroke\\\": \\\"#DEE0E3\\\", \\\"strokeWidth\\\": 0.5, \\\"fill\\\": \\\"#ffffff\\\", \\\"magnet\\\": true}, \\\"portNameLabel\\\": {\\\"ref\\\": \\\"portBody\\\", \\\"refX\\\": 12, \\\"refY\\\": 9.5, \\\"fontSize\\\": 13, \\\"fontWeight\\\": 500, \\\"textAnchor\\\": \\\"left\\\", \\\"fill\\\": \\\"#1F2329\\\", \\\"textWrap\\\": {\\\"width\\\": 120, \\\"height\\\": 20, \\\"ellipsis\\\": true}}}, \\\"position\\\": \\\"erPortPosition\\\"}}, \\\"items\\\": [{\\\"id\\\": \\\"port-35-334\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"part_id\\\"}}}, {\\\"id\\\": \\\"port-35-335\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"part_name\\\"}}}, {\\\"id\\\": \\\"port-35-336\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"location_id\\\"}}}, {\\\"id\\\": \\\"port-35-337\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"part_model\\\"}}}, {\\\"id\\\": \\\"port-35-338\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"category\\\"}}}, {\\\"id\\\": \\\"port-35-339\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"spare_part_status\\\"}}}, {\\\"id\\\": \\\"port-35-340\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"spare_part_type\\\"}}}, {\\\"id\\\": \\\"port-35-341\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"sn\\\"}}}, {\\\"id\\\": \\\"port-35-342\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"manufacturer\\\"}}}, {\\\"id\\\": \\\"port-35-343\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"unit\\\"}}}, {\\\"id\\\": \\\"port-35-344\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"status\\\"}}}]}, \\\"id\\\": \\\"node-35\\\", \\\"zIndex\\\": 1}, {\\\"position\\\": {\\\"x\\\": 550, \\\"y\\\": 650}, \\\"size\\\": {\\\"width\\\": 200, \\\"height\\\": 411}, \\\"attrs\\\": {\\\"text\\\": {\\\"text\\\": \\\"stockout\\\"}}, \\\"visible\\\": true, \\\"shape\\\": \\\"er-rect\\\", \\\"ports\\\": {\\\"groups\\\": {\\\"list\\\": {\\\"markup\\\": [{\\\"tagName\\\": \\\"rect\\\", \\\"selector\\\": \\\"portBody\\\"}, {\\\"tagName\\\": \\\"text\\\", \\\"selector\\\": \\\"portNameLabel\\\"}], \\\"attrs\\\": {\\\"portBody\\\": {\\\"width\\\": 200, \\\"height\\\": 36, \\\"stroke\\\": \\\"#DEE0E3\\\", \\\"strokeWidth\\\": 0.5, \\\"fill\\\": \\\"#ffffff\\\", \\\"magnet\\\": true}, \\\"portNameLabel\\\": {\\\"ref\\\": \\\"portBody\\\", \\\"refX\\\": 12, \\\"refY\\\": 9.5, \\\"fontSize\\\": 13, \\\"fontWeight\\\": 500, \\\"textAnchor\\\": \\\"left\\\", \\\"fill\\\": \\\"#1F2329\\\", \\\"textWrap\\\": {\\\"width\\\": 120, \\\"height\\\": 20, \\\"ellipsis\\\": true}}}, \\\"position\\\": \\\"erPortPosition\\\"}}, \\\"items\\\": [{\\\"id\\\": \\\"port-36-345\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"id\\\"}}}, {\\\"id\\\": \\\"port-36-346\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"request_id\\\"}}}, {\\\"id\\\": \\\"port-36-347\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"part_name\\\"}}}, {\\\"id\\\": \\\"port-36-348\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"part_model\\\"}}}, {\\\"id\\\": \\\"port-36-349\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"sn\\\"}}}, {\\\"id\\\": \\\"port-36-350\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"operator_id\\\"}}}, {\\\"id\\\": \\\"port-36-351\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"location_id\\\"}}}, {\\\"id\\\": \\\"port-36-352\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"out_time\\\"}}}, {\\\"id\\\": \\\"port-36-353\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"status\\\"}}}, {\\\"id\\\": \\\"port-36-354\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"location_name\\\"}}}]}, \\\"id\\\": \\\"node-36\\\", \\\"zIndex\\\": 1}, {\\\"position\\\": {\\\"x\\\": -210, \\\"y\\\": 820}, \\\"size\\\": {\\\"width\\\": 200, \\\"height\\\": 375}, \\\"attrs\\\": {\\\"text\\\": {\\\"text\\\": \\\"transfer_record\\\"}}, \\\"visible\\\": true, \\\"shape\\\": \\\"er-rect\\\", \\\"ports\\\": {\\\"groups\\\": {\\\"list\\\": {\\\"markup\\\": [{\\\"tagName\\\": \\\"rect\\\", \\\"selector\\\": \\\"portBody\\\"}, {\\\"tagName\\\": \\\"text\\\", \\\"selector\\\": \\\"portNameLabel\\\"}], \\\"attrs\\\": {\\\"portBody\\\": {\\\"width\\\": 200, \\\"height\\\": 36, \\\"stroke\\\": \\\"#DEE0E3\\\", \\\"strokeWidth\\\": 0.5, \\\"fill\\\": \\\"#ffffff\\\", \\\"magnet\\\": true}, \\\"portNameLabel\\\": {\\\"ref\\\": \\\"portBody\\\", \\\"refX\\\": 12, \\\"refY\\\": 9.5, \\\"fontSize\\\": 13, \\\"fontWeight\\\": 500, \\\"textAnchor\\\": \\\"left\\\", \\\"fill\\\": \\\"#1F2329\\\", \\\"textWrap\\\": {\\\"width\\\": 120, \\\"height\\\": 20, \\\"ellipsis\\\": true}}}, \\\"position\\\": \\\"erPortPosition\\\"}}, \\\"items\\\": [{\\\"id\\\": \\\"port-37-355\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"transfer_id\\\"}}}, {\\\"id\\\": \\\"port-37-356\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"from_location_name\\\"}}}, {\\\"id\\\": \\\"port-37-357\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"to_location_name\\\"}}}, {\\\"id\\\": \\\"port-37-358\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"part_name\\\"}}}, {\\\"id\\\": \\\"port-37-359\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"sn\\\"}}}, {\\\"id\\\": \\\"port-37-360\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"transfer_reason\\\"}}}, {\\\"id\\\": \\\"port-37-361\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"applicant_id\\\"}}}, {\\\"id\\\": \\\"port-37-362\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"status\\\"}}}, {\\\"id\\\": \\\"port-37-363\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"created_at\\\"}}}]}, \\\"id\\\": \\\"node-37\\\", \\\"zIndex\\\": 1}, {\\\"position\\\": {\\\"x\\\": 300, \\\"y\\\": 950}, \\\"size\\\": {\\\"width\\\": 200, \\\"height\\\": 375}, \\\"attrs\\\": {\\\"text\\\": {\\\"text\\\": \\\"usagerequest\\\"}}, \\\"visible\\\": true, \\\"shape\\\": \\\"er-rect\\\", \\\"ports\\\": {\\\"groups\\\": {\\\"list\\\": {\\\"markup\\\": [{\\\"tagName\\\": \\\"rect\\\", \\\"selector\\\": \\\"portBody\\\"}, {\\\"tagName\\\": \\\"text\\\", \\\"selector\\\": \\\"portNameLabel\\\"}], \\\"attrs\\\": {\\\"portBody\\\": {\\\"width\\\": 200, \\\"height\\\": 36, \\\"stroke\\\": \\\"#DEE0E3\\\", \\\"strokeWidth\\\": 0.5, \\\"fill\\\": \\\"#ffffff\\\", \\\"magnet\\\": true}, \\\"portNameLabel\\\": {\\\"ref\\\": \\\"portBody\\\", \\\"refX\\\": 12, \\\"refY\\\": 9.5, \\\"fontSize\\\": 13, \\\"fontWeight\\\": 500, \\\"textAnchor\\\": \\\"left\\\", \\\"fill\\\": \\\"#1F2329\\\", \\\"textWrap\\\": {\\\"width\\\": 120, \\\"height\\\": 20, \\\"ellipsis\\\": true}}}, \\\"position\\\": \\\"erPortPosition\\\"}}, \\\"items\\\": [{\\\"id\\\": \\\"port-38-364\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"id\\\"}}}, {\\\"id\\\": \\\"port-38-365\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"location_id\\\"}}}, {\\\"id\\\": \\\"port-38-366\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"applicant_id\\\"}}}, {\\\"id\\\": \\\"port-38-367\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"part_name\\\"}}}, {\\\"id\\\": \\\"port-38-368\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"part_model\\\"}}}, {\\\"id\\\": \\\"port-38-369\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"description\\\"}}}, {\\\"id\\\": \\\"port-38-370\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"type\\\"}}}, {\\\"id\\\": \\\"port-38-371\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"status\\\"}}}, {\\\"id\\\": \\\"port-38-372\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"create_time\\\"}}}]}, \\\"id\\\": \\\"node-38\\\", \\\"zIndex\\\": 1}, {\\\"position\\\": {\\\"x\\\": 550, \\\"y\\\": 950}, \\\"size\\\": {\\\"width\\\": 200, \\\"height\\\": 267}, \\\"attrs\\\": {\\\"text\\\": {\\\"text\\\": \\\"user\\\"}}, \\\"visible\\\": true, \\\"shape\\\": \\\"er-rect\\\", \\\"ports\\\": {\\\"groups\\\": {\\\"list\\\": {\\\"markup\\\": [{\\\"tagName\\\": \\\"rect\\\", \\\"selector\\\": \\\"portBody\\\"}, {\\\"tagName\\\": \\\"text\\\", \\\"selector\\\": \\\"portNameLabel\\\"}], \\\"attrs\\\": {\\\"portBody\\\": {\\\"width\\\": 200, \\\"height\\\": 36, \\\"stroke\\\": \\\"#DEE0E3\\\", \\\"strokeWidth\\\": 0.5, \\\"fill\\\": \\\"#ffffff\\\", \\\"magnet\\\": true}, \\\"portNameLabel\\\": {\\\"ref\\\": \\\"portBody\\\", \\\"refX\\\": 12, \\\"refY\\\": 9.5, \\\"fontSize\\\": 13, \\\"fontWeight\\\": 500, \\\"textAnchor\\\": \\\"left\\\", \\\"fill\\\": \\\"#1F2329\\\", \\\"textWrap\\\": {\\\"width\\\": 120, \\\"height\\\": 20, \\\"ellipsis\\\": true}}}, \\\"position\\\": \\\"erPortPosition\\\"}}, \\\"items\\\": [{\\\"id\\\": \\\"port-39-373\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"user_id\\\"}}}, {\\\"id\\\": \\\"port-39-374\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"name\\\"}}}, {\\\"id\\\": \\\"port-39-375\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"password\\\"}}}, {\\\"id\\\": \\\"port-39-376\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"role\\\"}}}, {\\\"id\\\": \\\"port-39-377\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"workshop\\\"}}}, {\\\"id\\\": \\\"port-39-378\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"contact\\\"}}}]}, \\\"id\\\": \\\"node-39\\\", \\\"zIndex\\\": 1}, {\\\"position\\\": {\\\"x\\\": 50, \\\"y\\\": 1250}, \\\"size\\\": {\\\"width\\\": 200, \\\"height\\\": 303}, \\\"attrs\\\": {\\\"text\\\": {\\\"text\\\": \\\"warehouse_location\\\"}}, \\\"visible\\\": true, \\\"shape\\\": \\\"er-rect\\\", \\\"ports\\\": {\\\"groups\\\": {\\\"list\\\": {\\\"markup\\\": [{\\\"tagName\\\": \\\"rect\\\", \\\"selector\\\": \\\"portBody\\\"}, {\\\"tagName\\\": \\\"text\\\", \\\"selector\\\": \\\"portNameLabel\\\"}], \\\"attrs\\\": {\\\"portBody\\\": {\\\"width\\\": 200, \\\"height\\\": 36, \\\"stroke\\\": \\\"#DEE0E3\\\", \\\"strokeWidth\\\": 0.5, \\\"fill\\\": \\\"#ffffff\\\", \\\"magnet\\\": true}, \\\"portNameLabel\\\": {\\\"ref\\\": \\\"portBody\\\", \\\"refX\\\": 12, \\\"refY\\\": 9.5, \\\"fontSize\\\": 13, \\\"fontWeight\\\": 500, \\\"textAnchor\\\": \\\"left\\\", \\\"fill\\\": \\\"#1F2329\\\", \\\"textWrap\\\": {\\\"width\\\": 120, \\\"height\\\": 20, \\\"ellipsis\\\": true}}}, \\\"position\\\": \\\"erPortPosition\\\"}}, \\\"items\\\": [{\\\"id\\\": \\\"port-40-379\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"location_id\\\"}}}, {\\\"id\\\": \\\"port-40-380\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"location_code\\\"}}}, {\\\"id\\\": \\\"port-40-381\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"location_name\\\"}}}, {\\\"id\\\": \\\"port-40-382\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"description\\\"}}}, {\\\"id\\\": \\\"port-40-383\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"status\\\"}}}, {\\\"id\\\": \\\"port-40-384\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"created_at\\\"}}}, {\\\"id\\\": \\\"port-40-385\\\", \\\"group\\\": \\\"list\\\", \\\"attrs\\\": {\\\"portNameLabel\\\": {\\\"text\\\": \\\"name\\\"}}}]}, \\\"id\\\": \\\"node-40\\\", \\\"zIndex\\\": 1}, {\\\"shape\\\": \\\"edge\\\", \\\"attrs\\\": {\\\"line\\\": {\\\"stroke\\\": \\\"#A8ADB4\\\", \\\"strokeWidth\\\": 1.5, \\\"targetMarker\\\": {\\\"name\\\": \\\"block\\\", \\\"width\\\": 12, \\\"height\\\": 8}}}, \\\"id\\\": \\\"8fee6e46-53fc-4526-81da-6dc91579efdd\\\", \\\"tools\\\": {\\\"items\\\": []}, \\\"source\\\": {\\\"cell\\\": \\\"node-29\\\", \\\"port\\\": \\\"port-29-272\\\"}, \\\"target\\\": {\\\"cell\\\": \\\"node-30\\\", \\\"port\\\": \\\"port-30-289\\\"}, \\\"zIndex\\\": 2}, {\\\"shape\\\": \\\"edge\\\", \\\"attrs\\\": {\\\"line\\\": {\\\"stroke\\\": \\\"#A8ADB4\\\", \\\"strokeWidth\\\": 1.5, \\\"targetMarker\\\": {\\\"name\\\": \\\"block\\\", \\\"width\\\": 12, \\\"height\\\": 8}}}, \\\"id\\\": \\\"81cc58b9-3c09-4cab-a21e-b34f3581e6b7\\\", \\\"tools\\\": {\\\"items\\\": []}, \\\"source\\\": {\\\"cell\\\": \\\"node-33\\\", \\\"port\\\": \\\"port-33-309\\\"}, \\\"target\\\": {\\\"cell\\\": \\\"node-32\\\", \\\"port\\\": \\\"port-32-304\\\"}, \\\"zIndex\\\": 3}, {\\\"shape\\\": \\\"edge\\\", \\\"attrs\\\": {\\\"line\\\": {\\\"stroke\\\": \\\"#A8ADB4\\\", \\\"strokeWidth\\\": 1.5, \\\"targetMarker\\\": {\\\"name\\\": \\\"block\\\", \\\"width\\\": 12, \\\"height\\\": 8}}}, \\\"id\\\": \\\"b0fb1bf2-0a04-4d1a-a711-240d84e2a45c\\\", \\\"tools\\\": {\\\"items\\\": []}, \\\"source\\\": {\\\"cell\\\": \\\"node-39\\\", \\\"port\\\": \\\"port-39-374\\\"}, \\\"target\\\": {\\\"cell\\\": \\\"node-38\\\", \\\"port\\\": \\\"port-38-365\\\"}, \\\"zIndex\\\": 4}, {\\\"shape\\\": \\\"edge\\\", \\\"attrs\\\": {\\\"line\\\": {\\\"stroke\\\": \\\"#A8ADB4\\\", \\\"strokeWidth\\\": 1.5, \\\"targetMarker\\\": {\\\"name\\\": \\\"block\\\", \\\"width\\\": 12, \\\"height\\\": 8}}}, \\\"id\\\": \\\"0f9c1861-3d5f-49cc-92ec-da7997314314\\\", \\\"tools\\\": {\\\"items\\\": []}, \\\"source\\\": {\\\"cell\\\": \\\"node-35\\\", \\\"port\\\": \\\"port-35-334\\\"}, \\\"target\\\": {\\\"cell\\\": \\\"node-36\\\", \\\"port\\\": \\\"port-36-346\\\"}, \\\"zIndex\\\": 5}]}\"');

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
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ds_id`(`ds_id` ASC) USING BTREE,
  INDEX `table_id`(`table_id` ASC) USING BTREE,
  CONSTRAINT `t_datasource_field_ibfk_1` FOREIGN KEY (`ds_id`) REFERENCES `t_datasource` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `t_datasource_field_ibfk_2` FOREIGN KEY (`table_id`) REFERENCES `t_datasource_table` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 386 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_as_ci COMMENT = '数据源字段信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_datasource_field
-- ----------------------------
INSERT INTO `t_datasource_field` VALUES (27, 1, 4, 1, 'id', 'int', '', NULL, 1);
INSERT INTO `t_datasource_field` VALUES (28, 1, 4, 1, 'workerid', 'int', '', NULL, 2);
INSERT INTO `t_datasource_field` VALUES (29, 1, 4, 1, 'workername', 'varchar(255)', '', NULL, 3);
INSERT INTO `t_datasource_field` VALUES (30, 1, 4, 1, 'product', 'int', '', NULL, 4);
INSERT INTO `t_datasource_field` VALUES (31, 1, 4, 1, 'pass', 'int', '', NULL, 5);
INSERT INTO `t_datasource_field` VALUES (32, 1, 4, 1, 'defective', 'int', '', NULL, 6);
INSERT INTO `t_datasource_field` VALUES (33, 1, 4, 1, 'disappear', 'int', '', NULL, 7);
INSERT INTO `t_datasource_field` VALUES (34, 1, 4, 1, 'datatime', 'datetime', '', NULL, 8);
INSERT INTO `t_datasource_field` VALUES (35, 1, 5, 1, 'id', 'int', '', NULL, 1);
INSERT INTO `t_datasource_field` VALUES (36, 1, 5, 1, 'name', 'varchar(255)', '', NULL, 2);
INSERT INTO `t_datasource_field` VALUES (37, 1, 5, 1, 'sex', 'enum(\'男\',\'女\')', '', NULL, 3);
INSERT INTO `t_datasource_field` VALUES (38, 1, 5, 1, 'year', 'int', '', NULL, 4);
INSERT INTO `t_datasource_field` VALUES (39, 1, 5, 1, 'xueyuan', 'varchar(255)', '', NULL, 5);
INSERT INTO `t_datasource_field` VALUES (40, 1, 5, 1, 'work', 'varchar(255)', '', NULL, 6);
INSERT INTO `t_datasource_field` VALUES (41, 1, 5, 1, 'classa', 'int', '', NULL, 7);
INSERT INTO `t_datasource_field` VALUES (42, 1, 5, 1, 'why', 'varchar(255)', '', NULL, 8);
INSERT INTO `t_datasource_field` VALUES (43, 1, 5, 1, 'datatime', 'varchar(255)', '', NULL, 9);
INSERT INTO `t_datasource_field` VALUES (254, 21, 28, 1, 'fault_id', 'bigint', '', NULL, 1);
INSERT INTO `t_datasource_field` VALUES (255, 21, 28, 1, 'part_id', 'int', '备件ID（关联备件表）', NULL, 2);
INSERT INTO `t_datasource_field` VALUES (256, 21, 28, 1, 'sn', 'varchar(255)', '备件SN号（冗余字段，方便查询）', NULL, 3);
INSERT INTO `t_datasource_field` VALUES (257, 21, 28, 1, 'fault_time', 'datetime', '故障发现时间', NULL, 4);
INSERT INTO `t_datasource_field` VALUES (258, 21, 28, 1, 'reported_by', 'varchar(255)', '故障报告人（现场工程师）', NULL, 5);
INSERT INTO `t_datasource_field` VALUES (259, 21, 28, 1, 'fault_description', 'text', '故障现象描述', NULL, 6);
INSERT INTO `t_datasource_field` VALUES (260, 21, 28, 1, 'work_order_status', 'enum(\'处理中\',\'已关闭\',\'已报废\',\'已返厂\',\'已验收\',\'待处理\',\'待验收\')', '', NULL, 7);
INSERT INTO `t_datasource_field` VALUES (261, 21, 28, 1, 'repair_result', 'varchar(255)', '维修结果描述', NULL, 8);
INSERT INTO `t_datasource_field` VALUES (262, 21, 28, 1, 'repair_by', 'varchar(255)', '维修人员（二级维修人员）', NULL, 9);
INSERT INTO `t_datasource_field` VALUES (263, 21, 28, 1, 'processed_at', 'datetime', '维修完成时间', NULL, 10);
INSERT INTO `t_datasource_field` VALUES (264, 21, 28, 1, 'review_result', 'enum(\'通过\',\'驳回\')', '', NULL, 11);
INSERT INTO `t_datasource_field` VALUES (265, 21, 28, 1, 'review_by', 'varchar(255)', '验收人（库管）', NULL, 12);
INSERT INTO `t_datasource_field` VALUES (266, 21, 28, 1, 'review_at', 'datetime', '验收时间', NULL, 13);
INSERT INTO `t_datasource_field` VALUES (267, 21, 28, 1, 'disposal_type', 'enum(\'修好件\',\'报废\',\'返厂修\')', '', NULL, 14);
INSERT INTO `t_datasource_field` VALUES (268, 21, 28, 1, 'created_at', 'datetime', '工单创建时间', NULL, 15);
INSERT INTO `t_datasource_field` VALUES (269, 21, 29, 1, 'inbound_id', 'int', '入库记录ID', NULL, 1);
INSERT INTO `t_datasource_field` VALUES (270, 21, 29, 1, 'order_id', 'int', '采购订单ID（外键）', NULL, 2);
INSERT INTO `t_datasource_field` VALUES (271, 21, 29, 1, 'location_id', 'int', '仓库ID（外键）', NULL, 3);
INSERT INTO `t_datasource_field` VALUES (272, 21, 29, 1, 'spare_part_category', 'enum(\'其他\',\'机械类\',\'液压类\',\'电子类\',\'电气类\')', '', NULL, 4);
INSERT INTO `t_datasource_field` VALUES (273, 21, 29, 1, 'spare_part_status', 'enum(\'二级修\',\'修好件\',\'坏件\',\'已报废\',\'待报废\',\'待调拨\',\'新好件\',\'返厂修\')', '', NULL, 5);
INSERT INTO `t_datasource_field` VALUES (274, 21, 29, 1, 'spare_part_type', 'enum(\'在保件\',\'正常件\',\'遗留件\')', '', NULL, 6);
INSERT INTO `t_datasource_field` VALUES (275, 21, 29, 1, 'unit_price', 'decimal(10,2)', '单价', NULL, 7);
INSERT INTO `t_datasource_field` VALUES (276, 21, 29, 1, 'tax_rate', 'decimal(5,2)', '税率（如0.13）', NULL, 8);
INSERT INTO `t_datasource_field` VALUES (277, 21, 29, 1, 'tax_free_unit_price', 'decimal(10,2)', '不含税单价', NULL, 9);
INSERT INTO `t_datasource_field` VALUES (278, 21, 29, 1, 'tax_amount', 'decimal(10,2)', '税额', NULL, 10);
INSERT INTO `t_datasource_field` VALUES (279, 21, 29, 1, 'tax_free_total', 'decimal(12,2)', '不含税总额', NULL, 11);
INSERT INTO `t_datasource_field` VALUES (280, 21, 29, 1, 'total_tax', 'decimal(12,2)', '总税额', NULL, 12);
INSERT INTO `t_datasource_field` VALUES (281, 21, 29, 1, 'sn', 'varchar(100)', '', NULL, 13);
INSERT INTO `t_datasource_field` VALUES (282, 21, 29, 1, 'unit', 'varchar(20)', '单位（如个/台/米）', NULL, 14);
INSERT INTO `t_datasource_field` VALUES (283, 21, 29, 1, 'manufacturer', 'varchar(100)', '生产厂家', NULL, 15);
INSERT INTO `t_datasource_field` VALUES (284, 21, 29, 1, 'warranty_until', 'date', '保修期至', NULL, 16);
INSERT INTO `t_datasource_field` VALUES (285, 21, 29, 1, 'created_at', 'datetime', '创建时间', NULL, 17);
INSERT INTO `t_datasource_field` VALUES (286, 21, 30, 1, 'inventory_id', 'int', '库存记录ID', NULL, 1);
INSERT INTO `t_datasource_field` VALUES (287, 21, 30, 1, 'part_name', 'varchar(255)', '备件名称', NULL, 2);
INSERT INTO `t_datasource_field` VALUES (288, 21, 30, 1, 'location_name', 'varchar(255)', '', NULL, 3);
INSERT INTO `t_datasource_field` VALUES (289, 21, 30, 1, 'status', 'varchar(255)', '状态', NULL, 4);
INSERT INTO `t_datasource_field` VALUES (290, 21, 30, 1, 'number', 'varchar(255)', '当前数量', NULL, 5);
INSERT INTO `t_datasource_field` VALUES (291, 21, 30, 1, 'safety_stock', 'int', '安全库存阈值', NULL, 6);
INSERT INTO `t_datasource_field` VALUES (292, 21, 31, 1, 'order_id', 'int', '采购订单ID', NULL, 1);
INSERT INTO `t_datasource_field` VALUES (293, 21, 31, 1, 'applicant_id', 'int', '申请人ID（外键）', NULL, 2);
INSERT INTO `t_datasource_field` VALUES (294, 21, 31, 1, 'station', 'varchar(255)', '需求车站', NULL, 3);
INSERT INTO `t_datasource_field` VALUES (295, 21, 31, 1, 'workshop', 'varchar(255)', '所属工区', NULL, 4);
INSERT INTO `t_datasource_field` VALUES (296, 21, 31, 1, 'status', 'varchar(255)', '状态', NULL, 5);
INSERT INTO `t_datasource_field` VALUES (297, 21, 31, 1, 'spare_part_name', 'varchar(255)', '备件名称', NULL, 6);
INSERT INTO `t_datasource_field` VALUES (298, 21, 31, 1, 'spare_part_model', 'varchar(255)', '备件型号', NULL, 7);
INSERT INTO `t_datasource_field` VALUES (299, 21, 31, 1, 'number', 'varchar(255)', '数量', NULL, 8);
INSERT INTO `t_datasource_field` VALUES (300, 21, 31, 1, 'created_at', 'varchar(255)', '创建时间', NULL, 9);
INSERT INTO `t_datasource_field` VALUES (301, 21, 31, 1, 'completed_at', 'varchar(255)', '完成时间', NULL, 10);
INSERT INTO `t_datasource_field` VALUES (302, 21, 32, 1, 'history_id', 'int', '', NULL, 1);
INSERT INTO `t_datasource_field` VALUES (303, 21, 32, 1, 'order_id', 'int', '', NULL, 2);
INSERT INTO `t_datasource_field` VALUES (304, 21, 32, 1, 'status', 'varchar(255)', '', NULL, 3);
INSERT INTO `t_datasource_field` VALUES (305, 21, 32, 1, 'changed_by', 'int', '', NULL, 4);
INSERT INTO `t_datasource_field` VALUES (306, 21, 32, 1, 'changed_at', 'datetime', '', NULL, 5);
INSERT INTO `t_datasource_field` VALUES (307, 21, 33, 1, 'return_id', 'int', '', NULL, 1);
INSERT INTO `t_datasource_field` VALUES (308, 21, 33, 1, 'actual_return_time', 'datetime(6)', '', NULL, 2);
INSERT INTO `t_datasource_field` VALUES (309, 21, 33, 1, 'created_at', 'datetime(6)', '', NULL, 3);
INSERT INTO `t_datasource_field` VALUES (310, 21, 33, 1, 'created_by', 'int', '', NULL, 4);
INSERT INTO `t_datasource_field` VALUES (311, 21, 33, 1, 'expected_repair_days', 'int', '', NULL, 5);
INSERT INTO `t_datasource_field` VALUES (312, 21, 33, 1, 'expected_return_time', 'datetime(6)', '', NULL, 6);
INSERT INTO `t_datasource_field` VALUES (313, 21, 33, 1, 'fault_id', 'bigint', '', NULL, 7);
INSERT INTO `t_datasource_field` VALUES (314, 21, 33, 1, 'logistics_company', 'varchar(100)', '', NULL, 8);
INSERT INTO `t_datasource_field` VALUES (315, 21, 33, 1, 'logistics_number', 'varchar(100)', '', NULL, 9);
INSERT INTO `t_datasource_field` VALUES (316, 21, 33, 1, 'part_id', 'int', '', NULL, 10);
INSERT INTO `t_datasource_field` VALUES (317, 21, 33, 1, 'repair_description', 'text', '', NULL, 11);
INSERT INTO `t_datasource_field` VALUES (318, 21, 33, 1, 'repair_result', 'enum(\'修复成功\',\'修复失败\',\'未修复\')', '', NULL, 12);
INSERT INTO `t_datasource_field` VALUES (319, 21, 33, 1, 'return_reason', 'text', '', NULL, 13);
INSERT INTO `t_datasource_field` VALUES (320, 21, 33, 1, 'sent_time', 'datetime(6)', '', NULL, 14);
INSERT INTO `t_datasource_field` VALUES (321, 21, 33, 1, 'sn', 'varchar(255)', '', NULL, 15);
INSERT INTO `t_datasource_field` VALUES (322, 21, 33, 1, 'status', 'enum(\'待返厂\',\'已返厂\',\'维修中\',\'已返回\',\'已验收\',\'已报废\')', '', NULL, 16);
INSERT INTO `t_datasource_field` VALUES (323, 21, 33, 1, 'updated_at', 'datetime(6)', '', NULL, 17);
INSERT INTO `t_datasource_field` VALUES (324, 21, 34, 1, 'order_id', 'int', '', NULL, 1);
INSERT INTO `t_datasource_field` VALUES (325, 21, 34, 1, 'applicant_id', 'varchar(255)', '', NULL, 2);
INSERT INTO `t_datasource_field` VALUES (326, 21, 34, 1, 'apply_time', 'varchar(255)', '', NULL, 3);
INSERT INTO `t_datasource_field` VALUES (327, 21, 34, 1, 'damage_photo', 'varchar(255)', '', NULL, 4);
INSERT INTO `t_datasource_field` VALUES (328, 21, 34, 1, 'disposal_method', 'varchar(255)', '', NULL, 5);
INSERT INTO `t_datasource_field` VALUES (329, 21, 34, 1, 'executor', 'varchar(255)', '', NULL, 6);
INSERT INTO `t_datasource_field` VALUES (330, 21, 34, 1, 'part_status', 'enum(\'待审核\',\'已报废\',\'驳回\')', '', NULL, 7);
INSERT INTO `t_datasource_field` VALUES (331, 21, 34, 1, 'scrap_reason', 'varchar(255)', '', NULL, 8);
INSERT INTO `t_datasource_field` VALUES (332, 21, 34, 1, 'scrap_time', 'varchar(255)', '', NULL, 9);
INSERT INTO `t_datasource_field` VALUES (333, 21, 34, 1, 'sn', 'varchar(255)', '', NULL, 10);
INSERT INTO `t_datasource_field` VALUES (334, 21, 35, 1, 'part_id', 'int', '', NULL, 1);
INSERT INTO `t_datasource_field` VALUES (335, 21, 35, 1, 'part_name', 'varchar(255)', '备件名称', NULL, 2);
INSERT INTO `t_datasource_field` VALUES (336, 21, 35, 1, 'location_id', 'int', '', NULL, 3);
INSERT INTO `t_datasource_field` VALUES (337, 21, 35, 1, 'part_model', 'varchar(255)', '备件型号', NULL, 4);
INSERT INTO `t_datasource_field` VALUES (338, 21, 35, 1, 'category', 'enum(\'机械类\',\'电气类\',\'液压类\',\'电子类\',\'其他\')', '', NULL, 5);
INSERT INTO `t_datasource_field` VALUES (339, 21, 35, 1, 'spare_part_status', 'enum(\'新好件\',\'修好件\',\'坏件\',\'二级修\',\'返厂修\',\'待调拨\',\'已报废\')', '', NULL, 6);
INSERT INTO `t_datasource_field` VALUES (340, 21, 35, 1, 'spare_part_type', 'enum(\'正常件\',\'在保件\',\'遗留件\')', '', NULL, 7);
INSERT INTO `t_datasource_field` VALUES (341, 21, 35, 1, 'sn', 'varchar(255)', '', NULL, 8);
INSERT INTO `t_datasource_field` VALUES (342, 21, 35, 1, 'manufacturer', 'varchar(255)', '生产厂家', NULL, 9);
INSERT INTO `t_datasource_field` VALUES (343, 21, 35, 1, 'unit', 'varchar(255)', '单位', NULL, 10);
INSERT INTO `t_datasource_field` VALUES (344, 21, 35, 1, 'status', 'varchar(255)', '是否在库', NULL, 11);
INSERT INTO `t_datasource_field` VALUES (345, 21, 36, 1, 'id', 'int', '出库id', NULL, 1);
INSERT INTO `t_datasource_field` VALUES (346, 21, 36, 1, 'request_id', 'int', '关联领用单', NULL, 2);
INSERT INTO `t_datasource_field` VALUES (347, 21, 36, 1, 'part_name', 'varchar(255)', '备件名称', NULL, 3);
INSERT INTO `t_datasource_field` VALUES (348, 21, 36, 1, 'part_model', 'varchar(255)', '备件型号', NULL, 4);
INSERT INTO `t_datasource_field` VALUES (349, 21, 36, 1, 'sn', 'varchar(255)', '备件SN', NULL, 5);
INSERT INTO `t_datasource_field` VALUES (350, 21, 36, 1, 'operator_id', 'int', '出库操作员', NULL, 6);
INSERT INTO `t_datasource_field` VALUES (351, 21, 36, 1, 'location_id', 'varchar(255)', '仓库ID', NULL, 7);
INSERT INTO `t_datasource_field` VALUES (352, 21, 36, 1, 'out_time', 'varchar(255)', '出库时间', NULL, 8);
INSERT INTO `t_datasource_field` VALUES (353, 21, 36, 1, 'status', 'varchar(255)', '出库状态', NULL, 9);
INSERT INTO `t_datasource_field` VALUES (354, 21, 36, 1, 'location_name', 'varchar(255)', '出库仓库', NULL, 10);
INSERT INTO `t_datasource_field` VALUES (355, 21, 37, 1, 'transfer_id', 'int', '调拨记录ID', NULL, 1);
INSERT INTO `t_datasource_field` VALUES (356, 21, 37, 1, 'from_location_name', 'varchar(255)', '', NULL, 2);
INSERT INTO `t_datasource_field` VALUES (357, 21, 37, 1, 'to_location_name', 'varchar(255)', '', NULL, 3);
INSERT INTO `t_datasource_field` VALUES (358, 21, 37, 1, 'part_name', 'varchar(255)', '备件名称', NULL, 4);
INSERT INTO `t_datasource_field` VALUES (359, 21, 37, 1, 'sn', 'varchar(255)', '备件SN', NULL, 5);
INSERT INTO `t_datasource_field` VALUES (360, 21, 37, 1, 'transfer_reason', 'varchar(255)', '调拨事由', NULL, 6);
INSERT INTO `t_datasource_field` VALUES (361, 21, 37, 1, 'applicant_id', 'int', '申请人ID（外键）', NULL, 7);
INSERT INTO `t_datasource_field` VALUES (362, 21, 37, 1, 'status', 'varchar(255)', '状态', NULL, 8);
INSERT INTO `t_datasource_field` VALUES (363, 21, 37, 1, 'created_at', 'varchar(255)', '创建时间', NULL, 9);
INSERT INTO `t_datasource_field` VALUES (364, 21, 38, 1, 'id', 'int', '领用单号', NULL, 1);
INSERT INTO `t_datasource_field` VALUES (365, 21, 38, 1, 'location_id', 'int', '出库ID', NULL, 2);
INSERT INTO `t_datasource_field` VALUES (366, 21, 38, 1, 'applicant_id', 'int', '申请人', NULL, 3);
INSERT INTO `t_datasource_field` VALUES (367, 21, 38, 1, 'part_name', 'varchar(255)', '', NULL, 4);
INSERT INTO `t_datasource_field` VALUES (368, 21, 38, 1, 'part_model', 'varchar(255)', '备件型号', NULL, 5);
INSERT INTO `t_datasource_field` VALUES (369, 21, 38, 1, 'description', 'varchar(255)', '申请说明', NULL, 6);
INSERT INTO `t_datasource_field` VALUES (370, 21, 38, 1, 'type', 'enum(\'维修申领\',\'维修借用\')', '类型', NULL, 7);
INSERT INTO `t_datasource_field` VALUES (371, 21, 38, 1, 'status', 'varchar(255)', '状态', NULL, 8);
INSERT INTO `t_datasource_field` VALUES (372, 21, 38, 1, 'create_time', 'varchar(255)', '创建时间', NULL, 9);
INSERT INTO `t_datasource_field` VALUES (373, 21, 39, 1, 'user_id', 'int', '用户ID', NULL, 1);
INSERT INTO `t_datasource_field` VALUES (374, 21, 39, 1, 'name', 'varchar(255)', '用户名称', NULL, 2);
INSERT INTO `t_datasource_field` VALUES (375, 21, 39, 1, 'password', 'varchar(255)', '密码', NULL, 3);
INSERT INTO `t_datasource_field` VALUES (376, 21, 39, 1, 'role', 'varchar(255)', '角色', NULL, 4);
INSERT INTO `t_datasource_field` VALUES (377, 21, 39, 1, 'workshop', 'varchar(255)', '所属工区', NULL, 5);
INSERT INTO `t_datasource_field` VALUES (378, 21, 39, 1, 'contact', 'varchar(255)', '联系方式', NULL, 6);
INSERT INTO `t_datasource_field` VALUES (379, 21, 40, 1, 'location_id', 'int', '', NULL, 1);
INSERT INTO `t_datasource_field` VALUES (380, 21, 40, 1, 'location_code', 'varchar(255)', '仓库编码', NULL, 2);
INSERT INTO `t_datasource_field` VALUES (381, 21, 40, 1, 'location_name', 'varchar(255)', '', NULL, 3);
INSERT INTO `t_datasource_field` VALUES (382, 21, 40, 1, 'description', 'varchar(255)', '库位描述（如位置、容量）', NULL, 4);
INSERT INTO `t_datasource_field` VALUES (383, 21, 40, 1, 'status', 'varchar(255)', '状态', NULL, 5);
INSERT INTO `t_datasource_field` VALUES (384, 21, 40, 1, 'created_at', 'varchar(255)', '创建时间', NULL, 6);
INSERT INTO `t_datasource_field` VALUES (385, 21, 40, 1, 'name', 'varchar(255)', '库管人', NULL, 7);

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
) ENGINE = InnoDB AUTO_INCREMENT = 41 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_as_ci COMMENT = '数据源表信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_datasource_table
-- ----------------------------
INSERT INTO `t_datasource_table` VALUES (4, 1, 1, 'daily', '', NULL, NULL);
INSERT INTO `t_datasource_table` VALUES (5, 1, 1, 'dailya', 'std请假表', 'std请假表', NULL);
INSERT INTO `t_datasource_table` VALUES (28, 21, 1, 'fault_order', '备件故障工单表', NULL, NULL);
INSERT INTO `t_datasource_table` VALUES (29, 21, 1, 'inbound_record', '入库记录表（含财务信息）', NULL, NULL);
INSERT INTO `t_datasource_table` VALUES (30, 21, 1, 'inventory', '库存记录表', NULL, NULL);
INSERT INTO `t_datasource_table` VALUES (31, 21, 1, 'purchase_order', '采购订单表', NULL, NULL);
INSERT INTO `t_datasource_table` VALUES (32, 21, 1, 'purchase_order_status_history', '', NULL, NULL);
INSERT INTO `t_datasource_table` VALUES (33, 21, 1, 'return_factory_record', '', NULL, NULL);
INSERT INTO `t_datasource_table` VALUES (34, 21, 1, 'scrap_records', '', NULL, NULL);
INSERT INTO `t_datasource_table` VALUES (35, 21, 1, 'spare_part', '备件基础信息表', NULL, NULL);
INSERT INTO `t_datasource_table` VALUES (36, 21, 1, 'stockout', '出库记录表', NULL, NULL);
INSERT INTO `t_datasource_table` VALUES (37, 21, 1, 'transfer_record', '调拨记录表', NULL, NULL);
INSERT INTO `t_datasource_table` VALUES (38, 21, 1, 'usagerequest', '领用申请表', NULL, NULL);
INSERT INTO `t_datasource_table` VALUES (39, 21, 1, 'user', '用户表', NULL, NULL);
INSERT INTO `t_datasource_table` VALUES (40, 21, 1, 'warehouse_location', '仓库信息表', NULL, NULL);

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
  `sql_statement` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT 'SQL语句（数据问答时保存）',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_conversation_id`(`conversation_id` ASC) USING BTREE,
  INDEX `idx_datasource_id`(`datasource_id` ASC) USING BTREE,
  INDEX `idx_create_time`(`create_time` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '问答记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_user_qa_record
-- ----------------------------

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

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, '张同宁', '123456', '2026-01-31 10:57:40', '2026-01-31 10:57:40');
INSERT INTO `users` VALUES (2, '臧博涛', '123456', '2026-01-31 10:57:53', '2026-01-31 10:57:53');
INSERT INTO `users` VALUES (3, '黄俊泽', '123456', '2026-01-31 10:58:03', '2026-01-31 10:58:03');
INSERT INTO `users` VALUES (4, '杨宗霖', '123456', '2026-01-31 10:58:25', '2026-01-31 10:58:25');

SET FOREIGN_KEY_CHECKS = 1;
