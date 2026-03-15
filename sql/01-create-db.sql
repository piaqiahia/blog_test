-- 创建测试数据库
CREATE DATABASE IF NOT EXISTS h3blog_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 授予权限
GRANT ALL PRIVILEGES ON h3blog_test.* TO 'root'@'%';
FLUSH PRIVILEGES;

-- 使用测试数据库
USE h3blog_test;