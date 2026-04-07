-- MySQL dump 10.13  Distrib 5.7.40, for Win64 (x86_64)
--
-- Host: localhost    Database: h3blog
-- ------------------------------------------------------
-- Server version	5.7.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cms_article`
--
DROP TABLE IF EXISTS `cms_article`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_article` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(120) DEFAULT NULL COMMENT '标题',
  `name` varchar(64) DEFAULT NULL COMMENT '编码',
  `editor` varchar(10) NOT NULL COMMENT '编辑器',
  `content` text COMMENT 'md内容',
  `content_html` text COMMENT '内容',
  `summary` varchar(300) DEFAULT NULL COMMENT '简述',
  `thumbnail` varchar(200) DEFAULT NULL COMMENT '缩略图',
  `state` int(11) DEFAULT NULL COMMENT '状态',
  `vc` int(11) DEFAULT NULL COMMENT '访问统计',
  `toc` text COMMENT '目录',
  `comment_num` int(11) NOT NULL,
  `publish_time` datetime DEFAULT NULL COMMENT '发布时间',
  `author` varchar(64) NOT NULL COMMENT '作者',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `category_id` int(11) DEFAULT NULL,
  `h_content` text NOT NULL,
  `h_role` int(11) DEFAULT NULL COMMENT '0=无,1=管理员,2=会员,3=vip, 4=付费',
  `price` decimal(10,2) DEFAULT NULL COMMENT '单价',
  `sn` int(11) NOT NULL COMMENT '排序',
  `is_crawl` int(11) DEFAULT NULL COMMENT '是否抓取内容',
  `origin_url` varchar(200) DEFAULT NULL COMMENT '抓取内容的原始url',
  `origin_author` varchar(100) DEFAULT NULL COMMENT '原作者',
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `org_id` int(11) DEFAULT NULL COMMENT '机构id',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_cms_article_name` (`name`),
  KEY `category_id` (`category_id`),
  KEY `ix_cms_article_publish_time` (`publish_time`),
  KEY `ix_cms_article_title` (`title`),
  CONSTRAINT `cms_article_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `cms_category` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_article`
--

LOCK TABLES `cms_article` WRITE;
/*!40000 ALTER TABLE `cms_article` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_article` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_article_tag`
--

DROP TABLE IF EXISTS `cms_article_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_article_tag` (
  `article_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  PRIMARY KEY (`article_id`,`tag_id`),
  KEY `tag_id` (`tag_id`),
  CONSTRAINT `cms_article_tag_ibfk_1` FOREIGN KEY (`article_id`) REFERENCES `cms_article` (`id`) ON DELETE CASCADE,
  CONSTRAINT `cms_article_tag_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `cms_tag` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_article_tag`
--

LOCK TABLES `cms_article_tag` WRITE;
/*!40000 ALTER TABLE `cms_article_tag` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_article_tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_baaner`
--

DROP TABLE IF EXISTS `cms_baaner`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_baaner` (
  `name` varchar(64) NOT NULL COMMENT '名称',
  `mtype` varchar(32) NOT NULL COMMENT '类型',
  `img` varchar(220) NOT NULL COMMENT '图片',
  `video` varchar(500) NOT NULL COMMENT '视频地址',
  `url` varchar(300) NOT NULL COMMENT '链接',
  `remark` varchar(300) NOT NULL COMMENT '备注',
  `order_num` int(11) DEFAULT NULL COMMENT '排序',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  `org_id` int(11) DEFAULT NULL COMMENT '机构id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_baaner`
--

LOCK TABLES `cms_baaner` WRITE;
/*!40000 ALTER TABLE `cms_baaner` DISABLE KEYS */;
INSERT INTO `cms_baaner` VALUES ('banner1','','/admin/uploads/demo/31572497460166656.png','','','',0,1,'2025-10-26 22:56:58',NULL,'2025-10-26 22:56:58','',0,NULL);
/*!40000 ALTER TABLE `cms_baaner` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_category`
--

DROP TABLE IF EXISTS `cms_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(64) DEFAULT NULL COMMENT '栏目标题',
  `parent_id` int(11) DEFAULT NULL COMMENT '父ID',
  `name` varchar(64) DEFAULT NULL COMMENT '编码',
  `desp` text COMMENT '栏目描述',
  `tpl_list` varchar(300) DEFAULT NULL COMMENT '列表模板',
  `tpl_page` varchar(300) DEFAULT NULL COMMENT '单页/详情模板',
  `tpl_mold` varchar(20) DEFAULT NULL COMMENT '模板类型 list,single_page',
  `content` text COMMENT '可以录入信息内容',
  `seo_title` varchar(100) DEFAULT NULL COMMENT 'seo标题',
  `seo_description` varchar(300) DEFAULT NULL COMMENT 'seo描述',
  `seo_keywords` varchar(300) DEFAULT NULL COMMENT 'seo关键词',
  `order_num` int(11) DEFAULT NULL COMMENT '排序',
  `visible` int(11) DEFAULT NULL COMMENT '是否隐藏',
  `icon` varchar(128) DEFAULT NULL,
  `img` varchar(300) DEFAULT NULL COMMENT '栏目图片',
  `h_role` int(11) DEFAULT NULL COMMENT '0=无,1=管理员,2=会员,3=vip, 4=付费',
  `price` decimal(10,2) DEFAULT NULL COMMENT '单价',
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `org_id` int(11) DEFAULT NULL COMMENT '机构id',
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id`),
  KEY `ix_cms_category_name` (`name`),
  KEY `ix_cms_category_title` (`title`),
  CONSTRAINT `cms_category_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `cms_category` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_category`
--

LOCK TABLES `cms_category` WRITE;
/*!40000 ALTER TABLE `cms_category` DISABLE KEYS */;
INSERT INTO `cms_category` VALUES (1,'Python',NULL,'python',NULL,'subject_list.html','subject_detail.html','list',NULL,NULL,NULL,NULL,1,1,'fa fa-address-book',NULL,0,0.00,'2025-10-26 22:56:58',NULL,'2025-10-26 22:56:58','',0,'',NULL),(2,'Java',NULL,'java',NULL,'subject_list.html','subject_detail.html','list',NULL,NULL,NULL,NULL,2,1,'fa fa-balance-scale',NULL,0,0.00,'2025-10-26 22:56:58',NULL,'2025-10-26 22:56:58','',0,'',NULL);
/*!40000 ALTER TABLE `cms_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_comment`
--

DROP TABLE IF EXISTS `cms_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `article_id` int(11) NOT NULL COMMENT '关联的文章id',
  `content` varchar(1024) DEFAULT NULL,
  `reply_id` int(11) DEFAULT NULL COMMENT '回复对应的评论id',
  `timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `article_id` (`article_id`),
  KEY `reply_id` (`reply_id`),
  CONSTRAINT `cms_comment_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `cms_comment_ibfk_2` FOREIGN KEY (`article_id`) REFERENCES `cms_article` (`id`),
  CONSTRAINT `cms_comment_ibfk_3` FOREIGN KEY (`reply_id`) REFERENCES `cms_comment` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_comment`
--

LOCK TABLES `cms_comment` WRITE;
/*!40000 ALTER TABLE `cms_comment` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_comment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_friendly_link`
--

DROP TABLE IF EXISTS `cms_friendly_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_friendly_link` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `link` varchar(200) NOT NULL COMMENT '连接',
  `name` varchar(200) NOT NULL COMMENT '名称',
  `state` int(11) DEFAULT NULL COMMENT '状态',
  `ctime` datetime DEFAULT NULL COMMENT '时间',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `org_id` int(11) DEFAULT NULL COMMENT '机构id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_friendly_link`
--

LOCK TABLES `cms_friendly_link` WRITE;
/*!40000 ALTER TABLE `cms_friendly_link` DISABLE KEYS */;
INSERT INTO `cms_friendly_link` VALUES (1,'https://www.h3blog.com','何三笔记',1,'2025-10-26 22:56:58',NULL,'2025-10-26 22:56:58','',0,'何三笔记',NULL);
/*!40000 ALTER TABLE `cms_friendly_link` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_material`
--

DROP TABLE IF EXISTS `cms_material`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_material` (
  `name` varchar(64) DEFAULT NULL COMMENT '名称',
  `mtype` varchar(32) DEFAULT NULL COMMENT '类型',
  `url` varchar(120) DEFAULT NULL COMMENT '文件',
  `remark` varchar(32) DEFAULT NULL COMMENT '备注',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  `org_id` int(11) DEFAULT NULL COMMENT '机构id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_material`
--

LOCK TABLES `cms_material` WRITE;
/*!40000 ALTER TABLE `cms_material` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_material` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_online_tool`
--

DROP TABLE IF EXISTS `cms_online_tool`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_online_tool` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(120) DEFAULT NULL,
  `desp` varchar(120) DEFAULT NULL,
  `img` varchar(200) DEFAULT NULL,
  `url` varchar(200) DEFAULT NULL,
  `sn` int(11) DEFAULT NULL,
  `state` int(11) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_online_tool`
--

LOCK TABLES `cms_online_tool` WRITE;
/*!40000 ALTER TABLE `cms_online_tool` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_online_tool` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_tag`
--

DROP TABLE IF EXISTS `cms_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL COMMENT '名称',
  `code` varchar(64) NOT NULL COMMENT '编码',
  `visible` int(11) DEFAULT NULL COMMENT '是否可见',
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `org_id` int(11) DEFAULT NULL COMMENT '机构id',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_cms_tag_code` (`code`),
  UNIQUE KEY `ix_cms_tag_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_tag`
--

LOCK TABLES `cms_tag` WRITE;
/*!40000 ALTER TABLE `cms_tag` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_theme`
--

DROP TABLE IF EXISTS `cms_theme`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_theme` (
  `name` varchar(64) NOT NULL COMMENT '主题名称',
  `code` varchar(64) NOT NULL COMMENT '主题代码',
  `description` varchar(300) NOT NULL COMMENT '主题描述',
  `preview_img` varchar(200) NOT NULL COMMENT '预览图片',
  `author` varchar(64) NOT NULL COMMENT '作者',
  `version` varchar(20) NOT NULL COMMENT '版本号',
  `is_active` int(11) NOT NULL COMMENT '是否激活(0=否,1=是)',
  `sn` int(11) NOT NULL COMMENT '排序',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `org_id` int(11) DEFAULT NULL COMMENT '机构id',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_cms_theme_code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_theme`
--

LOCK TABLES `cms_theme` WRITE;
/*!40000 ALTER TABLE `cms_theme` DISABLE KEYS */;
INSERT INTO `cms_theme` VALUES ('Tend','tend','Tend 主题','','系统','1.0.0',0,0,1,'2025-10-26 23:01:02',1,'2025-10-26 23:07:50',NULL,0,'',1),('Test','test','Test 主题','','系统','1.0.0',1,0,2,'2025-10-26 23:01:02',1,'2025-10-26 23:07:50',NULL,0,'',1);
/*!40000 ALTER TABLE `cms_theme` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gen_column`
--

DROP TABLE IF EXISTS `gen_column`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gen_column` (
  `gen_model_id` int(11) DEFAULT NULL COMMENT 'gen_model_id',
  `col_name` varchar(200) NOT NULL COMMENT '列名称',
  `col_comment` varchar(200) NOT NULL COMMENT '列描述',
  `col_type` varchar(200) NOT NULL COMMENT '列类型',
  `is_required` int(11) NOT NULL COMMENT '是否必填',
  `is_insert` int(11) NOT NULL COMMENT '是否插入字段',
  `is_edit` int(11) NOT NULL COMMENT '是否编辑字段',
  `is_list` int(11) NOT NULL COMMENT '是否列表字段',
  `is_query` int(11) NOT NULL COMMENT '是否查询字段',
  `query_type` varchar(200) NOT NULL COMMENT '查询方式（等于、不等于、大于、小于、范围）',
  `html_type` varchar(200) NOT NULL COMMENT '显示类型（文本框、文本域、下拉框、复选框、单选框、日期控件）',
  `order_num` int(11) NOT NULL COMMENT '排序',
  `dict_type` varchar(200) NOT NULL COMMENT '字典类型',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `org_id` int(11) DEFAULT NULL COMMENT '机构id',
  PRIMARY KEY (`id`),
  KEY `gen_model_id` (`gen_model_id`),
  CONSTRAINT `gen_column_ibfk_1` FOREIGN KEY (`gen_model_id`) REFERENCES `gen_model` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gen_column`
--

LOCK TABLES `gen_column` WRITE;
/*!40000 ALTER TABLE `gen_column` DISABLE KEYS */;
/*!40000 ALTER TABLE `gen_column` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gen_model`
--

DROP TABLE IF EXISTS `gen_model`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gen_model` (
  `name` varchar(200) NOT NULL COMMENT '名称',
  `model` varchar(64) NOT NULL COMMENT '模块',
  `model_name` varchar(64) NOT NULL COMMENT '模块名称',
  `tpl_path` varchar(120) NOT NULL COMMENT '模板路径',
  `view_path` varchar(120) NOT NULL COMMENT 'view路径',
  `tpl_category` varchar(120) NOT NULL COMMENT '模板类型',
  `tree_code` varchar(64) NOT NULL COMMENT '树字段编码',
  `tree_parent_code` varchar(64) NOT NULL COMMENT '树父字段编码',
  `tree_name` varchar(64) NOT NULL COMMENT '树名称字段',
  `tree_order` varchar(64) NOT NULL COMMENT '排序字段',
  `parent_menu_id` int(11) DEFAULT NULL COMMENT '父菜单id',
  `parent_menu_name` varchar(64) NOT NULL COMMENT '父菜单名称',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `org_id` int(11) DEFAULT NULL COMMENT '机构id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gen_model`
--

LOCK TABLES `gen_model` WRITE;
/*!40000 ALTER TABLE `gen_model` DISABLE KEYS */;
/*!40000 ALTER TABLE `gen_model` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invitation_code`
--

DROP TABLE IF EXISTS `invitation_code`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `invitation_code` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(64) NOT NULL,
  `user` varchar(64) DEFAULT NULL,
  `state` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invitation_code`
--

LOCK TABLES `invitation_code` WRITE;
/*!40000 ALTER TABLE `invitation_code` DISABLE KEYS */;
/*!40000 ALTER TABLE `invitation_code` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `member`
--

DROP TABLE IF EXISTS `member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `member` (
  `status` int(11) NOT NULL COMMENT '0正常 1停用',
  `name` varchar(64) NOT NULL COMMENT '姓名',
  `org_id` int(11) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mobile` varchar(32) DEFAULT NULL COMMENT '手机号',
  `username` varchar(64) DEFAULT NULL COMMENT '账号',
  `password_hash` varchar(256) DEFAULT NULL COMMENT '密码',
  `nickname` varchar(100) NOT NULL COMMENT '别名',
  `avatar` varchar(120) DEFAULT NULL COMMENT '头像',
  `last_seen` datetime DEFAULT NULL COMMENT '最后登陆时间',
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_member_username` (`username`),
  KEY `org_id` (`org_id`),
  CONSTRAINT `member_ibfk_1` FOREIGN KEY (`org_id`) REFERENCES `org` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `member`
--

LOCK TABLES `member` WRITE;
/*!40000 ALTER TABLE `member` DISABLE KEYS */;
/*!40000 ALTER TABLE `member` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `org`
--

DROP TABLE IF EXISTS `org`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `org` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL COMMENT '名称',
  `parent_id` int(11) DEFAULT NULL COMMENT '父ID',
  `order_num` int(11) DEFAULT NULL COMMENT '排序',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id`),
  CONSTRAINT `org_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `org` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `org`
--

LOCK TABLES `org` WRITE;
/*!40000 ALTER TABLE `org` DISABLE KEYS */;
INSERT INTO `org` VALUES (1,'默认',NULL,0,0);
/*!40000 ALTER TABLE `org` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pay_log`
--

DROP TABLE IF EXISTS `pay_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pay_log` (
  `pay_type` varchar(100) NOT NULL COMMENT '支付类型',
  `action_type` varchar(100) NOT NULL COMMENT '动作类型',
  `order_no` varchar(128) NOT NULL COMMENT '订单号',
  `subject` varchar(300) NOT NULL COMMENT '商品描述',
  `trade_no` varchar(300) NOT NULL COMMENT '交易订单号',
  `total_fee` decimal(10,2) DEFAULT NULL COMMENT '支付金额',
  `state` int(11) NOT NULL COMMENT '支付状态',
  `return_code` varchar(300) NOT NULL COMMENT '支付回调信息返回码',
  `return_data` varchar(5000) NOT NULL COMMENT '返回信息',
  `return_time` datetime DEFAULT NULL COMMENT '回调时间',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `ref_id` int(11) DEFAULT NULL COMMENT '关联id',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `org_id` int(11) DEFAULT NULL COMMENT '机构id',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_pay_log_order_no` (`order_no`),
  KEY `create_by` (`create_by`),
  CONSTRAINT `pay_log_ibfk_1` FOREIGN KEY (`create_by`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pay_log`
--

LOCK TABLES `pay_log` WRITE;
/*!40000 ALTER TABLE `pay_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `pay_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `setting`
--

DROP TABLE IF EXISTS `setting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `setting` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sname` varchar(128) NOT NULL COMMENT '参数名称',
  `skey` varchar(64) DEFAULT NULL COMMENT '参数键名',
  `svalue` text NOT NULL COMMENT '参数键值',
  `stype` varchar(2) NOT NULL COMMENT '系统内置',
  `col_type` varchar(64) NOT NULL COMMENT '输入类型',
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `org_id` int(11) DEFAULT NULL COMMENT '机构id',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_setting_skey` (`skey`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `setting`
--

LOCK TABLES `setting` WRITE;
/*!40000 ALTER TABLE `setting` DISABLE KEYS */;
INSERT INTO `setting` VALUES (1,'菜单导航显示风格','SYS_NAV_STYLE','topnav','','string','2025-10-26 22:56:58',NULL,'2025-10-26 22:56:58','',0,'菜单导航显示风格（default为左侧导航菜单，topnav为顶部导航菜单）',NULL),(2,'默认皮肤样式名称  ','SYS_SKIN_NAME','skin-red','','string','2025-10-26 22:56:58',NULL,'2025-10-26 22:56:58','',0,'蓝色 skin-blue、绿色 skin-green、紫色 skin-purple、红色 skin-red、黄色 skin-yellow',NULL),(3,'侧边栏主题','SYS_SIDE_THEME','theme-blue','','string','2025-10-26 22:56:58',NULL,'2025-10-26 22:56:58','',0,'深黑主题theme-dark，浅色主题theme-light，深蓝主题theme-blue',NULL),(4,'登陆背景图片','SYS_LOGIN_BACKGROUND','','','file','2025-10-26 22:56:58',NULL,'2025-10-26 22:56:58','',0,'登陆背景图片（2560x1600），默认default',NULL),(5,'允许上传的图片后缀','H3BLOG_ALLOWED_IMAGE_EXTENSIONS','png, jpg, jpeg, gif, webp,doc,docx,xls,xlsx,ppt,pptx, pdf,mp3, mp4,txt,zip,rar,z7','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'允许上传的图片后缀，多个值用逗号隔开',NULL),(6,'站点标题','H3BLOG_TITLE','何三笔记','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'站点标题',NULL),(7,'网站robots','H3BLOG_ROBOTS','User-agent: *\nAllow: /\n','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'网站robots',NULL),(8,'网站扩展meta','H3BLOG_EXTEND_META','','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'扩展meta,有的站长平台验证需要添加',NULL),(9,'网站统计代码','H3BLOG_TONGJI_SCRIPT','','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'统计代码',NULL),(10,'网站前端模板','H3BLOG_TEMPLATE','tend','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'模板名称',NULL),(11,'网站描述','H3BLOG_DESCRIPTION','分享python编程心得','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'网站描述',NULL),(12,'网站SEO关键词','H3BLOG_KEYWORDS','python,java,linux','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'网站关键字',NULL),(13,'网站域名','H3BLOG_DOMAIN','','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'网站域名',NULL),(14,'网站左侧悬浮导航','H3BLOG_NAVBAR','on','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'on=开启，off=关闭',NULL),(15,'默认编辑器','H3BLOG_EDITOR','markdown','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'编辑器支持：tinymce、markdown',NULL),(16,'ICP备案号','H3BLOG_ICP','ICP备XXXXX','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'ICP备案号',NULL),(17,'公安网安备案号','H3BLOG_GWAB','XXXXXX','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'公安网安备案号',NULL),(18,'网站开始时间 ','H3BLOG_START_TIME','2025-10-26','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'网站开始时间，网站底部显示',NULL),(19,'网站地图URL生成模式前缀','SITEMAP_URL_SCHEME','https','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'网站协议 https, http',NULL),(20,'七牛云SecretKey','QINIU_SECRET_KEY','','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'七牛云SecretKey',NULL),(21,'七牛云AccessKey','QINIU_ACCESS_KEY','','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'七牛云AccessKey',NULL),(22,'七牛云bucket名称','QINIU_BUCKET_NAME','','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'七牛云bucket名称',NULL),(23,'七牛云CDN域名','QINIU_CDN_URL','','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'七牛云CDN域名',NULL),(24,'文件上传存储方式','H3BLOG_UPLOAD_TYPE','local','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'上传方式，local=本地，qiniu=七牛云',NULL),(25,'SMTP服务器','H3BLOG_SMTP_SERVER','smtp.163.com','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'SMTP服务器',NULL),(26,'SMTP用户名','H3BLOG_SMTP_USER','','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'SMTP用户名',NULL),(27,'邮件smtp密码或授权码','H3BLOG_SMTP_PWD_AUTH','','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'邮件smtp密码或授权码,看邮件平台支持情况来填',NULL),(28,'支付宝当面付appid','ALIPAY_APPID','','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'支付宝appid',NULL),(29,'支付宝当面付公钥','ALIPAY_PUBLIC_KEY','','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'支付宝公钥',NULL),(30,'支付宝当面付私钥','ALIPAY_PRIVATE_KEY','','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'支付宝私钥',NULL),(31,'支付宝当面付异步通知url','ALIPAY_NOTIFY_URL','http://www.XXXXXX.com/alipay_nofity','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'支付宝当面付异步通知url',NULL),(32,'支付宝当面付沙箱调试','ALIPAY_SENDBOX_DEBUG','FALSE','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'支付宝当面付沙箱调试，FALSE=关闭，TRUE=开启',NULL),(33,'会员充值金额','VIP_AMOUNT','299','','string','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'会员充值金额',NULL);
/*!40000 ALTER TABLE `setting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_dict_data`
--

DROP TABLE IF EXISTS `sys_dict_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sys_dict_data` (
  `sort` int(11) DEFAULT NULL COMMENT '字典顺序',
  `label` varchar(100) NOT NULL COMMENT '字典标签',
  `value` varchar(100) NOT NULL COMMENT '字典键值',
  `dict_type` varchar(100) NOT NULL COMMENT '字典类型',
  `css_class` varchar(100) NOT NULL COMMENT '样式属性（其他样式扩展）',
  `list_class` varchar(100) NOT NULL COMMENT '表格回显样式',
  `is_default` varchar(1) DEFAULT NULL COMMENT '是否默认（Y是 N否）',
  `status` int(11) DEFAULT NULL COMMENT '状态(0正常 1停用',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `org_id` int(11) DEFAULT NULL COMMENT '机构id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_dict_data`
--

LOCK TABLES `sys_dict_data` WRITE;
/*!40000 ALTER TABLE `sys_dict_data` DISABLE KEYS */;
INSERT INTO `sys_dict_data` VALUES (1,'是','Y','sys_setting_stype','','','Y',0,1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(1,'否','N','sys_setting_stype','','','N',0,2,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(1,'管理员','admin','sys_user_type','','','N',0,3,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(2,'会员','member','sys_user_type','','','Y',0,4,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(1,'可见','1','cms_visible','','','Y',0,5,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(2,'隐藏','0','cms_visible','','','N',0,6,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(1,'单页','single_page','cms_category_tpl_mold','','','N',0,7,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(2,'列表页','list','cms_category_tpl_mold','','','Y',0,8,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(1,'图片','pic','cms_material_type','','','Y',0,9,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(2,'视频','video','cms_material_type','','','N',0,10,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(1,'草稿','0','cms_article_state','','','Y',0,11,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(2,'已发布','1','cms_article_state','','','N',0,12,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(1,'显示','1','tag_visible','','','Y',0,13,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(2,'隐藏','0','tag_visible','','','N',0,14,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(1,'未支付','0','paylog_state','','','Y',0,15,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(1,'成功','1','paylog_state','','','Y',0,16,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(1,'可用','1','cms_friendlylink_state','','','Y',0,17,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(1,'禁用','0','cms_friendlylink_state','','','N',0,18,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL);
/*!40000 ALTER TABLE `sys_dict_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_dict_type`
--

DROP TABLE IF EXISTS `sys_dict_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sys_dict_type` (
  `name` varchar(100) NOT NULL COMMENT '字典名称',
  `dict_type` varchar(100) NOT NULL COMMENT '字典类型',
  `status` int(11) DEFAULT NULL COMMENT '状态(0正常 1停用',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `org_id` int(11) DEFAULT NULL COMMENT '机构id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_dict_type`
--

LOCK TABLES `sys_dict_type` WRITE;
/*!40000 ALTER TABLE `sys_dict_type` DISABLE KEYS */;
INSERT INTO `sys_dict_type` VALUES ('系统参数类型','sys_setting_stype',0,1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),('用户类型','sys_user_type',0,2,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),('是否显示','cms_visible',0,3,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),('cms栏目模板类型','cms_category_tpl_mold',0,4,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),('素材资源类型','cms_material_type',0,5,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),('文章状态','cms_article_state',0,6,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),('Tag状态','tag_visible',0,7,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),('支付状态','paylog_state',0,8,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),('友情链接状态','cms_friendlylink_state',0,9,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL);
/*!40000 ALTER TABLE `sys_dict_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_login_log`
--

DROP TABLE IF EXISTS `sys_login_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sys_login_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `login_name` varchar(100) NOT NULL COMMENT '登录账号',
  `ipaddr` varchar(64) NOT NULL COMMENT '登录ip',
  `login_location` varchar(200) NOT NULL COMMENT '登录地点',
  `browser` varchar(200) NOT NULL COMMENT '浏览器类型',
  `ossystem` varchar(200) NOT NULL COMMENT '操作系统',
  `state` int(11) NOT NULL COMMENT '登录状态',
  `msg` varchar(200) NOT NULL COMMENT '提示消息',
  `login_time` datetime DEFAULT NULL COMMENT '访问时间',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_login_log`
--

LOCK TABLES `sys_login_log` WRITE;
/*!40000 ALTER TABLE `sys_login_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_login_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_menu`
--

DROP TABLE IF EXISTS `sys_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sys_menu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL COMMENT '菜单名称',
  `parent_id` int(11) DEFAULT NULL COMMENT '父菜单ID',
  `order_num` int(11) DEFAULT NULL COMMENT '显示排序',
  `url` varchar(200) DEFAULT NULL COMMENT '请求地址',
  `target` varchar(20) DEFAULT NULL COMMENT '打开方式(menuItem页签 menuBlank新窗口)',
  `menu_type` varchar(5) DEFAULT NULL COMMENT '菜单类型（M目录 C菜单 F按钮）',
  `visible` int(11) DEFAULT NULL COMMENT '菜单状态（0显示 1隐藏）',
  `perms` varchar(100) DEFAULT NULL COMMENT '权限标识',
  `icon` varchar(100) DEFAULT NULL COMMENT '菜单图标',
  `is_refresh` int(11) DEFAULT NULL COMMENT '是否刷新（0刷新 1不刷新）',
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `org_id` int(11) DEFAULT NULL COMMENT '机构id',
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id`),
  CONSTRAINT `sys_menu_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `sys_menu` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_menu`
--

LOCK TABLES `sys_menu` WRITE;
/*!40000 ALTER TABLE `sys_menu` DISABLE KEYS */;
INSERT INTO `sys_menu` VALUES (1,'系统管理',NULL,1,'','menuItem','M',0,'','fa fa-cog',0,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(2,'网站管理',NULL,0,'','menuItem','M',0,'','fa fa-bell-o',0,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(3,'系统工具',NULL,2,'','menuItem','M',0,'','fa fa-anchor',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(4,'用户管理',1,1,'/admin/sys/user/','menuItem','C',0,'user','fa fa-user',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(5,'角色权限',1,2,'/admin/sys/role/','menuItem','C',0,'role','fa fa-address-book',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(6,'菜单管理',1,3,'/admin/sys/menu/','menuItem','C',0,'menu','fa fa-calendar',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(7,'字典管理',1,4,'/admin/sys/dict_type/','menuItem','C',0,'dict_type','fa fa-bookmark-o',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(8,'系统参数',1,5,'/admin/sys/setting/','menuItem','C',0,'setting','fa fa-bookmark-o',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(9,'日志管理',1,6,'','menuItem','M',0,'','fa fa-bookmark-o',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(10,'栏目管理',2,3,'/admin/cms/category/','menuItem','C',0,'cms:category:view','fa fa-bath',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(11,'文章列表',2,2,'/admin/cms/article/','menuItem','C',0,'cms:article:view','fa fa-dashboard',0,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(12,'新增文章',2,1,'/admin/cms/article/edit','menuItem','C',0,'cms:article:add','fa fa-pencil',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(13,'素材管理',2,5,'/admin/cms/material/','menuItem','C',0,'cms:material:view','fa fa-image',0,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(14,'横幅管理',2,5,'/admin/cms/banner/','menuItem','C',0,'cms:banner:view','fa fa-cloud',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(15,'标签管理',2,4,'/admin/cms/tag/','menuItem','C',0,'cms:tag:view','fa fa-flag',0,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(16,'支付日志',2,6,'/admin/cms/paylog/','menuItem','C',0,'cms:paylog:view','fa fa-diamond',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(17,'友情链接',2,6,'/admin/cms/friendlylink/','menuItem','C',0,'cms:friendlylink:view','fa fa-handshake-o',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(18,'网站主题',2,7,'/admin/cms/theme/','menuItem','C',0,'cms:theme:view','fa fa-paint-brush',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(19,'预览网站',2,7,'/','menuBlank','C',0,'','fa fa-external-link',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(20,'代码生成',3,7,'/admin/sys/gencode/','menuItem','C',0,'gencode','fa fa-child',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(21,'查看',4,1,'','','F',1,'sys:user:view','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(22,'添加',4,2,'','','F',1,'sys:user:add','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(23,'修改',4,3,'','','F',1,'sys:user:edit','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(24,'删除',4,4,'','','F',1,'sys:user:remove','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(25,'重置密码',4,5,'','','F',1,'sys:user:reset_pwd','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(26,'查看',5,1,'','','F',1,'sys:role:view','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(27,'添加',5,2,'','','F',1,'sys:role:add','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(28,'修改',5,3,'','','F',1,'sys:role:edit','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(29,'删除',5,4,'','','F',1,'sys:role:remove','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(30,'查看',6,1,'','','F',1,'sys:menu:view','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(31,'添加',6,2,'','','F',1,'sys:menu:add','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(32,'修改',6,3,'','','F',1,'sys:menu:edit','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(33,'删除',6,4,'','','F',1,'sys:menu:remove','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(34,'查看',7,1,'','','F',1,'sys:dict_type:view','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(35,'添加',7,2,'','','F',1,'sys:dict_type:add','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(36,'修改',7,3,'','','F',1,'sys:dict_type:edit','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(37,'删除',7,4,'','','F',1,'sys:dict_type:remove','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(38,'查看',8,1,'','','F',1,'sys:setting:view','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(39,'添加',8,2,'','','F',1,'sys:setting:add','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(40,'修改',8,3,'','','F',1,'sys:setting:edit','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(41,'删除',8,4,'','','F',1,'sys:setting:remove','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(42,'登录日志',9,1,'/admin/sys/loginlog/','menuItem','C',0,'loginlog','fa fa-calendar-check-o',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(43,'操作日志',9,2,'/admin/sys/optlog/','menuItem','C',0,'optlog','fa fa-calendar-check-o',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(44,'添加',10,1,'#','','F',0,'cms:category:add','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(45,'修改',10,2,'#','','F',0,'cms:category:edit','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(46,'删除',10,3,'#','','F',0,'cms:category:remove','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(47,'添加',11,1,'#','','F',0,'cms:article:add','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(48,'修改',11,2,'#','','F',0,'cms:article:edit','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(49,'删除',11,3,'#','','F',0,'cms:article:remove','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(50,'添加',13,1,'#','','F',0,'cms:material:add','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(51,'修改',13,2,'#','','F',0,'cms:material:edit','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(52,'删除',13,3,'#','','F',0,'cms:material:remove','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(53,'添加',14,1,'#','','F',0,'cms:banner:add','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(54,'修改',14,2,'#','','F',0,'cms:banner:edit','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(55,'删除',14,3,'#','','F',0,'cms:banner:remove','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(56,'导出',14,4,'#','','F',0,'cms:banner:export','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(57,'添加',15,1,'#','','F',0,'cms:tag:add','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(58,'修改',15,2,'#','','F',0,'cms:tag:edit','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(59,'删除',15,3,'#','','F',0,'cms:tag:remove','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(60,'导出',15,4,'#','','F',0,'cms:tag:export','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(61,'添加',17,1,'','','F',0,'cms:friendlylink:add','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(62,'修改',17,2,'','','F',0,'cms:friendlylink:edit','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(63,'删除',17,3,'','','F',0,'cms:friendlylink:remove','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(64,'导出',17,4,'','','F',0,'cms:friendlylink:export','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(65,'添加',18,1,'#','','F',0,'cms:theme:add','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(66,'修改',18,2,'#','','F',0,'cms:theme:edit','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(67,'删除',18,3,'#','','F',0,'cms:theme:remove','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(68,'扫描',18,4,'#','','F',0,'cms:theme:scan','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL),(69,'激活',18,5,'#','','F',0,'cms:theme:activate','',1,'2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0,'',NULL);
/*!40000 ALTER TABLE `sys_menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_opt_log`
--

DROP TABLE IF EXISTS `sys_opt_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sys_opt_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL COMMENT '模块标题',
  `opt_name` varchar(100) NOT NULL COMMENT '操作',
  `method` varchar(50) NOT NULL COMMENT '方法名称',
  `oper_url` varchar(400) NOT NULL COMMENT '请求URL',
  `request_method` varchar(50) NOT NULL COMMENT '请求方式',
  `is_json_result` tinyint(1) NOT NULL COMMENT '是否是json结果',
  `oper_param` text COMMENT '请求参数',
  `json_result` text COMMENT '返回参数',
  `oper_name` varchar(100) NOT NULL COMMENT '操作人员',
  `ipaddr` varchar(64) NOT NULL COMMENT '主机地址',
  `login_location` varchar(200) NOT NULL COMMENT '操作地点',
  `browser` varchar(200) NOT NULL COMMENT '浏览器类型',
  `ossystem` varchar(200) NOT NULL COMMENT '操作系统',
  `state` int(11) NOT NULL COMMENT '操作状态',
  `msg` varchar(200) NOT NULL COMMENT '提示消息',
  `oper_time` datetime DEFAULT NULL COMMENT '访问时间',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_opt_log`
--

LOCK TABLES `sys_opt_log` WRITE;
/*!40000 ALTER TABLE `sys_opt_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_opt_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_role`
--

DROP TABLE IF EXISTS `sys_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sys_role` (
  `name` varchar(64) NOT NULL COMMENT '角色名称',
  `key` varchar(64) NOT NULL COMMENT '角色权限字符串',
  `sort` int(11) DEFAULT NULL COMMENT '显示顺序',
  `scope` int(11) DEFAULT NULL COMMENT '数据范围（1：超管权限 2：机构管理员权限 3: 代理权限）',
  `status` int(11) DEFAULT NULL COMMENT '角色状态(0正常 1停用',
  `org_id` int(11) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`),
  KEY `org_id` (`org_id`),
  CONSTRAINT `sys_role_ibfk_1` FOREIGN KEY (`org_id`) REFERENCES `org` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_role`
--

LOCK TABLES `sys_role` WRITE;
/*!40000 ALTER TABLE `sys_role` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_role_menu`
--

DROP TABLE IF EXISTS `sys_role_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sys_role_menu` (
  `role_id` int(11) NOT NULL,
  `menu_id` int(11) NOT NULL,
  PRIMARY KEY (`role_id`,`menu_id`),
  KEY `menu_id` (`menu_id`),
  CONSTRAINT `sys_role_menu_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sys_role_menu_ibfk_2` FOREIGN KEY (`menu_id`) REFERENCES `sys_menu` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_role_menu`
--

LOCK TABLES `sys_role_menu` WRITE;
/*!40000 ALTER TABLE `sys_role_menu` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_role_menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `email` varchar(64) DEFAULT NULL COMMENT '电子邮箱',
  `name` varchar(64) NOT NULL COMMENT '姓名',
  `sex` varchar(2) NOT NULL COMMENT '性别',
  `member_since` datetime DEFAULT NULL,
  `status` int(11) NOT NULL COMMENT '0正常 1停用',
  `user_type` varchar(64) DEFAULT NULL COMMENT 'admin=后台管理员',
  `role_id` int(11) DEFAULT NULL,
  `remark` varchar(200) DEFAULT NULL,
  `org_id` int(11) DEFAULT NULL,
  `vip_deadline` datetime DEFAULT NULL COMMENT '期限时间',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mobile` varchar(32) DEFAULT NULL COMMENT '手机号',
  `username` varchar(64) DEFAULT NULL COMMENT '账号',
  `password_hash` varchar(256) DEFAULT NULL COMMENT '密码',
  `nickname` varchar(100) NOT NULL COMMENT '别名',
  `avatar` varchar(120) DEFAULT NULL COMMENT '头像',
  `last_seen` datetime DEFAULT NULL COMMENT '最后登陆时间',
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_user_email` (`email`),
  UNIQUE KEY `ix_user_username` (`username`),
  KEY `role_id` (`role_id`),
  KEY `org_id` (`org_id`),
  CONSTRAINT `user_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`),
  CONSTRAINT `user_ibfk_2` FOREIGN KEY (`org_id`) REFERENCES `org` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES ('','管理员','','2025-10-26 14:56:59',0,'admin',NULL,'',1,'2025-10-26 22:56:59',1,NULL,'admin','scrypt:32768:8:1$XWOlbOHjzEDvD9U1$a29d016d48501b07ca1713867d2587fe0325704536d6e06d51a13782855e9030dd75ad635794294fc8444df9f2e1ca1f8c77a0ebc13d1e7509c9c79393c6b319','','','2025-10-26 14:56:59','2025-10-26 22:56:59',NULL,'2025-10-26 22:56:59','',0);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vip_price`
--

DROP TABLE IF EXISTS `vip_price`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vip_price` (
  `name` varchar(128) NOT NULL COMMENT '名称',
  `price` decimal(10,2) DEFAULT NULL COMMENT '支付金额',
  `days` int(11) NOT NULL COMMENT '天数',
  `desp` text NOT NULL COMMENT '描述',
  `sn` int(11) NOT NULL COMMENT '排序',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ctime` datetime DEFAULT NULL COMMENT '创建时间',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `utime` datetime DEFAULT NULL COMMENT '修改时间',
  `update_by` varchar(64) DEFAULT NULL COMMENT '修改者',
  `deleted` int(11) NOT NULL COMMENT '删除标记',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
  `org_id` int(11) DEFAULT NULL COMMENT '机构id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vip_price`
--

INSERT INTO cms_article (title, name, editor, content, content_html, summary, thumbnail, state, vc, toc, comment_num, publish_time, author, create_by, category_id, h_content, h_role, price, sn, is_crawl, origin_url, origin_author, ctime, utime, update_by, deleted, remark, org_id)
VALUES ('Flask 性能优化指南', 'flask-performance', 'admin', 'Flask 性能优化的详细指南...', '<p>Flask 性能优化的详细指南...</p>', '学习如何优化 Flask 应用性能', '/static/images/flask.jpg', 1, 1024, '[]', 5, '2024-01-15 10:00:00', '张三', 1, 1, '<p>Flask 性能优化的详细指南...</p>', 0, 99.00, 1, 0, NULL, NULL, '2024-01-15 10:00:00', '2024-01-15 10:00:00', 'admin', 0, '热门文章', 1);

-- 文章2
INSERT INTO cms_article (title, name, editor, content, content_html, summary, thumbnail, state, vc, toc, comment_num, publish_time, author, create_by, category_id, h_content, h_role, price, sn, is_crawl, origin_url, origin_author, ctime, utime, update_by, deleted, remark, org_id)
VALUES ('Python 并发编程', 'python-concurrency', 'admin', 'Python 并发编程的各种方法...', '<p>Python 并发编程的各种方法...</p>', '掌握 Python 并发编程技巧', '/static/images/python.jpg', 1, 2048, '[]', 12, '2024-01-16 11:00:00', '李四', 1, 2, '<p>Python 并发编程的各种方法...</p>', 0, 89.00, 2, 0, NULL, NULL, '2024-01-16 11:00:00', '2024-01-16 11:00:00', 'admin', 0, '推荐文章', 1);

-- 文章3
INSERT INTO cms_article (title, name, editor, content, content_html, summary, thumbnail, state, vc, toc, comment_num, publish_time, author, create_by, category_id, h_content, h_role, price, sn, is_crawl, origin_url, origin_author, ctime, utime, update_by, deleted, remark, org_id)
VALUES ('Docker 入门教程', 'docker-tutorial', 'admin', 'Docker 容器化技术入门...', '<p>Docker 容器化技术入门...</p>', '从零开始学习 Docker', '/static/images/docker.jpg', 1, 1536, '[]', 8, '2024-01-17 12:00:00', '王五', 1, 3, '<p>Docker 容器化技术入门...</p>', 0, 79.00, 3, 0, NULL, NULL, '2024-01-17 12:00:00', '2024-01-17 12:00:00', 'admin', 0, '新手必读', 1);

-- 文章4
INSERT INTO cms_article (title, name, editor, content, content_html, summary, thumbnail, state, vc, toc, comment_num, publish_time, author, create_by, category_id, h_content, h_role, price, sn, is_crawl, origin_url, origin_author, ctime, utime, update_by, deleted, remark, org_id)
VALUES ('MySQL 索引优化', 'mysql-index', 'admin', 'MySQL 索引优化最佳实践...', '<p>MySQL 索引优化最佳实践...</p>', '提升数据库查询性能', '/static/images/mysql.jpg', 1, 3072, '[]', 20, '2024-01-18 13:00:00', '赵六', 1, 4, '<p>MySQL 索引优化最佳实践...</p>', 0, 95.00, 4, 0, NULL, NULL, '2024-01-18 13:00:00', '2024-01-18 13:00:00', 'admin', 0, '数据库', 1);

-- 文章5
INSERT INTO cms_article (title, name, editor, content, content_html, summary, thumbnail, state, vc, toc, comment_num, publish_time, author, create_by, category_id, h_content, h_role, price, sn, is_crawl, origin_url, origin_author, ctime, utime, update_by, deleted, remark, org_id)
VALUES ('Redis 缓存策略', 'redis-cache', 'admin', 'Redis 缓存的各种策略...', '<p>Redis 缓存的各种策略...</p>', '高效使用 Redis 缓存', '/static/images/redis.jpg', 1, 2560, '[]', 15, '2024-01-19 14:00:00', '钱七', 1, 5, '<p>Redis 缓存的各种策略...</p>', 0, 85.00, 5, 0, NULL, NULL, '2024-01-19 14:00:00', '2024-01-19 14:00:00', 'admin', 0, '缓存', 1);

-- 文章6
INSERT INTO cms_article (title, name, editor, content, content_html, summary, thumbnail, state, vc, toc, comment_num, publish_time, author, create_by, category_id, h_content, h_role, price, sn, is_crawl, origin_url, origin_author, ctime, utime, update_by, deleted, remark, org_id)
VALUES ('Git 版本控制', 'git-version-control', 'admin', 'Git 版本控制系统使用指南...', '<p>Git 版本控制系统使用指南...</p>', '掌握 Git 的基本操作', '/static/images/git.jpg', 1, 1792, '[]', 10, '2024-01-20 15:00:00', '孙八', 1, 6, '<p>Git 版本控制系统使用指南...</p>', 0, 69.00, 6, 0, NULL, NULL, '2024-01-20 15:00:00', '2024-01-20 15:00:00', 'admin', 0, '工具', 1);

-- 文章7
INSERT INTO cms_article (title, name, editor, content, content_html, summary, thumbnail, state, vc, toc, comment_num, publish_time, author, create_by, category_id, h_content, h_role, price, sn, is_crawl, origin_url, origin_author, ctime, utime, update_by, deleted, remark, org_id)
VALUES ('Linux 命令大全', 'linux-commands', 'admin', '常用 Linux 命令汇总...', '<p>常用 Linux 命令汇总...</p>', 'Linux 日常命令速查', '/static/images/linux.jpg', 1, 4096, '[]', 25, '2024-01-21 16:00:00', '周九', 1, 7, '<p>常用 Linux 命令汇总...</p>', 0, 59.00, 7, 0, NULL, NULL, '2024-01-21 16:00:00', '2024-01-21 16:00:00', 'admin', 0, '运维', 1);

-- 文章8
INSERT INTO cms_article (title, name, editor, content, content_html, summary, thumbnail, state, vc, toc, comment_num, publish_time, author, create_by, category_id, h_content, h_role, price, sn, is_crawl, origin_url, origin_author, ctime, utime, update_by, deleted, remark, org_id)
VALUES ('机器学习入门', 'machine-learning', 'admin', '机器学习基础知识介绍...', '<p>机器学习基础知识介绍...</p>', 'AI 时代的必备技能', '/static/images/ml.jpg', 1, 5120, '[]', 30, '2024-01-22 17:00:00', '吴十', 1, 8, '<p>机器学习基础知识介绍...</p>', 0, 129.00, 8, 0, NULL, NULL, '2024-01-22 17:00:00', '2024-01-22 17:00:00', 'admin', 0, 'AI', 1);

-- 文章9
INSERT INTO cms_article (title, name, editor, content, content_html, summary, thumbnail, state, vc, toc, comment_num, publish_time, author, create_by, category_id, h_content, h_role, price, sn, is_crawl, origin_url, origin_author, ctime, utime, update_by, deleted, remark, org_id)
VALUES ('前端开发技巧', 'frontend-tips', 'admin', '前端开发的实用技巧分享...', '<p>前端开发的实用技巧分享...</p>', '提升前端开发效率', '/static/images/frontend.jpg', 1, 1280, '[]', 6, '2024-01-23 18:00:00', '郑十一', 1, 9, '<p>前端开发的实用技巧分享...</p>', 0, 75.00, 9, 0, NULL, NULL, '2024-01-23 18:00:00', '2024-01-23 18:00:00', 'admin', 0, '前端', 1);

-- 文章10
INSERT INTO cms_article (title, name, editor, content, content_html, summary, thumbnail, state, vc, toc, comment_num, publish_time, author, create_by, category_id, h_content, h_role, price, sn, is_crawl, origin_url, origin_author, ctime, utime, update_by, deleted, remark, org_id)
VALUES ('云计算架构', 'cloud-architecture', 'admin', '云计算架构设计原理...', '<p>云计算架构设计原理...</p>', '理解云计算的核心概念', '/static/images/cloud.jpg', 1, 2048, '[]', 14, '2024-01-24 19:00:00', '王十二', 1, 10, '<p>云计算架构设计原理...</p>', 0, 119.00, 10, 0, NULL, NULL, '2024-01-24 19:00:00', '2024-01-24 19:00:00', 'admin', 0, '云计算', 1);

LOCK TABLES `vip_price` WRITE;
/*!40000 ALTER TABLE `vip_price` DISABLE KEYS */;
/*!40000 ALTER TABLE `vip_price` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'h3blog'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-26 23:10:32
