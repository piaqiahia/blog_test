## 项目架构概述

H3Blog是一个基于Flask框架的现代化博客系统，采用模块化设计，具有清晰的前后端分离架构。项目采用蓝图(Blueprint)模式组织代码，支持多主题切换，具备完整的CMS功能。

### 核心架构特点
- **模块化设计**: 使用Flask蓝图将功能划分为main、admin、api三个主要模块
- **分层架构**: 清晰的Model-View-Controller模式，包含model、view、util等层次
- **主题系统**: 支持多主题切换，当前包含tend和test两个主题
- **数据库抽象**: 使用SQLAlchemy ORM，支持多种数据库后端

## 前端技术领域LLM提示词策略

### 1. 模板继承模式

**通用描述模板**:
```
本项目采用Jinja2模板引擎，使用模板继承机制。所有页面模板继承自base.html，通过block机制实现内容替换。

关键模板结构：
- base.html: 基础模板，定义页面整体结构和公共资源
- index.html: 首页模板，展示文章列表和轮播图
- article.html: 文章详情页，包含文章内容和评论区
- 宏组件: 通过_macros目录实现可复用组件
```

**LLM提示词示例**:
```
请为H3Blog项目创建一个新的文章分类页面模板，要求：
1. 继承自tend主题的base.html模板
2. 包含分类标题和文章列表展示
3. 使用分页组件显示文章列表
4. 遵循项目现有的CSS类命名规范
5. 使用宏组件实现分页功能
```

### 2. 组件化开发模式

**通用描述模板**:
```
项目采用组件化开发思想，通过Jinja2宏实现可复用组件：
- 分页组件(_patination.html): 标准分页控件
- 消息提示组件(_flash.html): 统一的消息提示样式
- 评论组件(_comment.html): 嵌套式评论系统

组件特点：
- 参数化设计，支持灵活配置
- 统一的样式规范
- 支持响应式布局
```

**LLM提示词示例**:
```
请为H3Blog项目创建一个新的标签云组件，要求：
1. 实现为Jinja2宏组件
2. 支持标签点击跳转功能
3. 根据标签使用频率调整字体大小
4. 遵循现有的CSS类命名规范
5. 支持响应式布局适配
```

### 3. 前端交互模式

**通用描述模板**:
```
前端交互采用AJAX + 传统表单提交混合模式：
- 用户认证相关使用传统表单提交
- 评论、点赞等交互使用AJAX
- 统一使用R类返回JSON格式数据
- 错误处理采用统一的提示机制

交互规范：
- 所有AJAX请求返回{code, msg, data}格式
- 错误码定义：0=成功，500=失败
- 使用Bootstrap模态框进行复杂交互
```

**LLM提示词示例**:
```
请为H3Blog项目实现文章收藏功能的前端交互，要求：
1. 使用AJAX实现收藏/取消收藏
2. 返回统一的JSON格式响应
3. 集成到现有的文章详情页面
4. 支持未登录用户的友好提示
5. 使用Bootstrap图标显示收藏状态
```

## 后端技术领域LLM提示词策略

### 1. 蓝图路由模式

**通用描述模板**:
```
项目采用Flask蓝图组织路由，分为三个主要蓝图：
- main: 前台博客功能
- admin: 后台管理系统
- api: API接口服务

路由定义规范：
- 使用@bp.route装饰器定义路由
- RESTful风格URL设计
- 统一的错误处理机制
- 支持URL参数和查询参数
```

**LLM提示词示例**:
```
请为H3Blog项目添加用户个人中心功能，要求：
1. 在main蓝图中添加相关路由
2. 实现个人信息查看和编辑功能
3. 使用@login_required装饰器保护路由
4. 遵循RESTful URL设计规范
5. 集成到现有的导航菜单中
```

### 2. 数据模型设计模式

**通用描述模板**:
```
数据模型采用SQLAlchemy ORM，具有以下特点：
- 继承BaseModel基类，包含通用字段
- 使用关系映射实现数据关联
- 支持软删除机制(deleted字段)
- 统一的审计字段(ctime, utime等)

模型设计规范：
- 所有模型继承自BaseModel或BaseUser
- 使用__tablename__明确指定表名
- 字段注释使用comment参数
- 关系定义使用relationship
```

**LLM提示词示例**:
```
请为H3Blog项目设计一个站内消息系统数据模型，要求：
1. 继承BaseModel基类
2. 包含发送者、接收者、消息内容等字段
3. 支持消息状态管理(已读/未读)
4. 实现与User模型的关联关系
5. 添加适当的索引优化查询性能
```

### 3. 业务逻辑处理模式

**通用描述模板**:
```
业务逻辑处理采用分层架构：
- Model层: 数据操作和业务规则
- View层: 请求处理和响应返回
- Util层: 通用工具函数

处理规范：
- 使用R类统一返回格式
- 异常处理使用try-catch块
- 数据库操作使用事务管理
- 业务验证使用表单验证
```

**LLM提示词示例**:
```
请为H3Blog项目实现文章搜索功能的后端逻辑，要求：
1. 支持标题和内容全文搜索
2. 实现分页显示搜索结果
3. 使用SQLAlchemy进行数据库查询
4. 返回统一的R类响应格式
5. 添加搜索关键词统计功能
```

## 模块间相似性模式分析

### 1. CRUD操作通用模式

**相似性特征**:
- 所有数据模型都支持标准的CRUD操作
- 使用统一的BaseModel提供基础功能
- 列表查询支持分页和排序
- 详情查询支持关联数据加载

**通用模板**:
```python
@bp.route('/<model_name>/list')
def list_<model_name>():
    # 查询逻辑
    items = <Model>.query.filter_by(deleted=0).paginate()
    return render_template(...)

@bp.route('/<model_name>/<int:id>')
def get_<model_name>(id):
    # 详情逻辑
    item = <Model>.query.get_or_404(id)
    return render_template(...)
```

### 2. 表单处理通用模式

**相似性特征**:
- 使用Flask-WTF进行表单验证
- 统一的错误处理机制
- 支持文件上传和数据处理
- 表单数据自动填充到模型

**通用模板**:
```python
@bp.route('/<model_name>/add', methods=['GET', 'POST'])
def add_<model_name>():
    form = <Model>Form()
    if form.validate_on_submit():
        # 数据处理逻辑
        item = <Model>()
        form.populate_obj(item)
        db.session.add(item)
        db.session.commit()
        return redirect(...)
    return render_template(...)
```

## 前后端交互逻辑标准化表达方法

### 1. API响应格式标准化

**标准格式**:
```json
{
    "code": 0,
    "msg": "操作成功",
    "data": {}
}
```

**LLM提示词规范**:
```
所有API接口必须返回统一的JSON格式，使用R类进行封装：
- 成功操作: R.success(data, msg)
- 失败操作: R.error(data, msg, code)
- 数据验证: 使用Flask-WTF表单验证
- 异常处理: 使用try-catch捕获异常
```

### 2. 错误处理标准化

**错误类型分类**:
- 客户端错误(4xx): 参数错误、权限不足等
- 服务器错误(5xx): 数据库异常、业务逻辑错误等
- 业务错误: 使用自定义错误码和消息

**处理规范**:
```python
try:
    # 业务逻辑
    return R.success(data)
except ValidationError as e:
    return R.error(msg="参数验证失败")
except Exception as e:
    logger.error(f"操作失败: {str(e)}")
    return R.error(msg="系统异常")
```

### 3. 数据验证标准化

**验证层次**:
1. 前端验证: HTML5表单验证
2. 后端验证: Flask-WTF表单验证
3. 业务验证: 自定义验证逻辑

**验证模板**:
```python
class ArticleForm(FlaskForm):
    title = StringField('标题', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    content = TextAreaField('内容', validators=[
        DataRequired()
    ])
```

## LLM提示词最佳实践

### 1. 上下文信息提供

**必要上下文**:
- 项目技术栈: Flask + SQLAlchemy + Jinja2
- 代码规范: PEP8 + 项目特定约定
- 架构模式: MVC + 蓝图 + 组件化
- 数据库设计: 软删除 + 审计字段

**提示词结构**:
```
基于H3Blog项目的技术架构，请实现以下功能：
[功能描述]

技术约束：
- 使用Flask蓝图模式
- 遵循现有的代码规范
- 使用SQLAlchemy进行数据操作
- 返回统一的R类响应
```

### 2. 约束条件明确

**技术约束**:
- Python 3.8+ 语法规范
- Flask扩展使用规范
- 数据库操作使用ORM
- 前端模板使用Jinja2语法

**业务约束**:
- 用户权限验证
- 数据完整性保证
- 性能优化考虑
- 安全性要求

### 3. 测试验证要求

**验证标准**:
- 功能完整性验证
- 代码规范检查
- 性能基准测试
- 安全漏洞扫描

## 总结

H3Blog项目的LLM提示词策略核心在于理解项目的模块化架构模式和编码规范。通过标准化的描述模板和明确的约束条件，可以有效引导LLM生成符合项目风格的代码。重点在于：

1. **架构一致性**: 保持与现有架构模式的一致性
2. **代码规范性**: 遵循项目的编码规范和命名约定
3. **功能完整性**: 确保生成代码的功能完整性和可维护性
4. **性能优化**: 考虑数据库查询性能和前端加载优化

通过系统性的提示词策略，可以显著提高LLM在H3Blog项目中的代码生成质量和开发效率。


# 运行项目

flask run --debug