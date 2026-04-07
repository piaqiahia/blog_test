CREATE DATABASE IF NOT EXISTS h3blog_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE h3blog_test;

-- 创建测试用的表结构（和上面一样）
CREATE TABLE IF NOT EXISTS category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS article (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    category_id INT
);