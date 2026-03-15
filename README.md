# h3blog

一个基于Python开发的轻量级博客系统 | A lightweight blog system based on Python


## 简介 | Introduction

h3blog是一个基于Python开发的轻量级博客系统，具有以下特点：
- 支持多模版切换
- SEO友好
- 快速开发框架
- 支持多数据库（SQLite、MySQL）
- 支持文章付费阅读
- 支持支付宝支付
  
博客界面参考: [https://www.h3blog.com](https://h3blog.com)

## 技术栈 | Tech Stack

- python
- flask
- flask-wtf
- flask-sqlalchemy
- markdown
- bootstrap4
- 支持sqlite、mysql（推荐）等

## 技术引用 | Tech References


- [ruoyi](https://gitee.com/y_project/RuoYi) 基于SpringBoot的权限管理系统
- [izone](https://github.com/Hopetree/izone) 一个基于Django的博客项目

## 功能特性 | Features

### 博客功能 | Blog Features
- 📝 文章管理 - 支持撰写、编辑、删除文章
- 📂 栏目管理 - 灵活的文章分类系统
- 🏷️ 标签管理 - 文章标签化管理
- 📁 素材管理 - 统一的媒体资源管理
- 🎯 横幅管理 - 自定义网站横幅
- 💰 支付日志 - 支付记录追踪
- 🔗 友链管理 - 友情链接维护

### 系统功能 | System Features
- 👥 用户管理 - 多用户支持
- 👑 角色管理 - 灵活的权限控制
- 📋 菜单管理 - 自定义后台菜单
- 📚 字典管理 - 系统参数字典
- ⚙️ 系统参数 - 全局配置管理
- 📊 登录日志 - 用户登录记录
- 📝 操作日志 - 系统操作追踪

## 环境要求 | Requirements

- Python 3.10+
- Git
- MySQL (推荐) 或 SQLite

## 快速开始 | Quick Start

### 1. 环境准备

确保您的系统已安装以下软件：
- Python 3.10 或更高版本
- Git
- MySQL (可选，推荐使用)

### 2. 获取源码

```bash
git clone https://gitee.com/pojoin/h3blog.git
cd h3blog
```

### 3. 配置Python环境

```bash
# 使用uv管理Python环境（推荐）
# 安装uv（如果尚未安装）
# Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Linux/Mac:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 使用uv创建虚拟环境并安装依赖
uv sync

# 激活虚拟环境
# Windows:
.\venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate
```

### 4. 数据库配置

#### MySQL配置（推荐）
```sql
# 创建数据库
CREATE DATABASE h3blog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 导入数据
mysql -u root -p h3blog < h3blog.sql
```

#### 环境配置
在项目根目录创建 `.env` 文件：
```env
# MySQL配置
DATABASE_URL = mysql+pymysql://root:your_password@127.0.0.1:3306/h3blog?charset=utf8mb4

# 或使用SQLite（不推荐生产环境）
# DATABASE_URL = sqlite:///h3blog.db
```

### 5. 启动应用

```bash
# 设置环境变量
# Windows PowerShell:
$env:FLASK_ENV="development"
# Windows CMD:
set FLASK_ENV=development
# Linux/Mac:
export FLASK_ENV=development

# 启动服务
flask run
```

### 6. 访问网站

- 博客首页：http://127.0.0.1:5000
- 管理后台：http://127.0.0.1:5000/admin  (默认用户名：admin，密码：123456)


## 部署说明 | Deployment
推荐使用 Gunicorn + Nginx 进行生产环境部署。详细部署文档请参考 (正在编写中...)。

## 界面示例 | Screenshots

![alt text](uploads/demo/blog/index.png)

![alt text](uploads/demo/blog/articles.png)

![alt text](uploads/demo/blog/banner.png)

![alt text](uploads/demo/blog/category.png)

![alt text](uploads/demo/blog/dict.png)

![alt text](uploads/demo/blog/edit.png)

![alt text](uploads/demo/blog/friedlylink.png)

![alt text](uploads/demo/blog/gencode.png)

![alt text](uploads/demo/blog/login_log.png)

![alt text](uploads/demo/blog/menu.png)

![alt text](uploads/demo/blog/optlog.png)

![alt text](uploads/demo/blog/pay.png)

![alt text](uploads/demo/blog/role.png)

![alt text](uploads/demo/blog/settings.png)

![alt text](uploads/demo/blog/sucai.png)

![alt text](uploads/demo/blog/tag.png)

![alt text](uploads/demo/blog/user.png)




## 贡献指南 | Contributing

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 许可证 | License

本项目采用 MIT 许可证，详情请参阅 [LICENSE](LICENSE) 文件。

## 联系方式 | Contact

如有问题或建议，请通过以下方式联系：
- Issue: [https://gitee.com/pojoin/h3blog/issues](https://gitee.com/pojoin/h3blog/issues)



##  `h3blog.sql` 文件下载

关注公众号“何三笔记”,回复`h3blog`即可获取h3blog.sql文件

![何三笔记公众号](app/main/themes/tend/static/img/qrcode_for_hesanbiji.jpg)
