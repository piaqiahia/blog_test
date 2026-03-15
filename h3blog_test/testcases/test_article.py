import allure
import time
import pytest
from datetime import datetime

@allure.feature("文章管理 - 新增修改")
@allure.title("文章管理-01: 管理员正常新增文章")
@allure.description("验证管理员会话下，用edit接口新增文章，验证文章的新增和删除")
@allure.severity(allure.severity_level.CRITICAL)
def test_article_add_success(admin_api):
    """正向新增 + 删除回归测试"""

    # 生成唯一标题（避免重复）
    unique_suffix = str(int(time.time()))
    title = f"自动化测试-{unique_suffix}"
    name = f"auto_test_{unique_suffix}"

    with allure.step("步骤1：调用edit接口新增文章"):
        admin_api.edit(
            title = title,
            name = name,
            editor = 'markdown',
            content = '1111',
            summary = '2222',
            h_role = 0,
            price = "0.00",  # 建议字符串
            h_content = '<p>3333</p>',  # 修复 HTML 标签闭合
            state = 1,
            category_id = 1,
            tagsinput = '4444',
            thumbnail = '/static/img/thumbnail.jpg',
            author = "管理员",
            vc = 0,
            publish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    with allure.step("步骤2：查询文章列表，验证新增文章"):
        result = admin_api.get_article(title = title)
        assert result["total"] >= 1, f"文章未创建成功，标题'{title}未在列表中发现'"
        article_id = result["rows"][0]["id"]
        allure.attach(
            str(article_id),               # 附件内容（必须是字符串）
            "新增文章ID",                   # 附件标题/名称 在 Allure 报告中显示为此名称
            allure.attachment_type.TEXT   # 附件类型 表示这是一个纯文本附件（也可以是 JSON、HTML、PNG 等）
        ) # 在测试报告中附加一个文本内容

    with allure.step("步骤3：删除该新增文章"):
        admin_api.remove(article_id)

    with allure.step("步骤4：验证文章是否删除"):
        del_info = admin_api.get_article(title = title)
        assert del_info["total"] == 0, "文章删除失败"

    allure.attach("全流程通过", "结果", allure.attachment_type.TEXT)

# 所有异常用例共用一个唯一前缀，避免污染
BASE_TITLE_PREFIX = "ParamTest_"

@allure.title("文章管理-02：新增文章异常场景参数化")
@pytest.mark.parametrize(
    "title, name, content, category_id, description",
    [
        ("", "empty_title", "内容正常", 1, "标题为空"),
        ("正常标题", "", "内容正常", 1, "name为空（唯一索引字段）"),
        ("正常标题", "normal_name", "", 1, "内容为空"),
        ("正常标题", "normal_name", "内容正常", 999, "分类ID不存在"),
        ("重复标题X", "duplicate_name_X", "内容正常", 1, "name重复（需先创建一次）"),
        ("<script>alert(1)</script>", "xss_name", "内容正常", 1, "标题含XSS脚本"),
        ("超长标题" + 'A' * 300, "long_name", "内容正常", 1, "标题过长（超过数据库限制）"),
        ("正常标题", "normal_name", "内容正常", -1, "分类ID为负数"),
        ("    ", "space_title", "内容正常", 1, "标题为空格"),
        ("正常标题", "normal_name", "内容正常", "abc", "分类ID为字符串（非数字）")
    ],
    ids = [
        "标题为空",
        "name为空",
        "内容为空",
        "分类ID不存在",
        "name重复",
        "标题含XSS脚本",
        "标题过长",
        "分类ID为负数",
        "标题为空格",
        "分类ID非数字"
    ]
)
def test_article_add_negative(admin_api, title, name, content, category_id, description):
    """参数化异常测试：验证各种非法输入不会创建文章"""

    # 为每个用例生成唯一标识，避免互相干扰
    unique = str(int(time.time() * 1000))
    test_title = f"{BASE_TITLE_PREFIX}{unique}_{title}" if title.strip() else f"{BASE_TITLE_PREFIX}{unique}_EMPTY"
    test_name = f"{BASE_TITLE_PREFIX}{unique}_name" if name.strip() else f"{BASE_TITLE_PREFIX}{unique}_EMPTY_NAME"

    with allure.step(f"准备数据：{description}"):
        # 特殊处理：'name重复' 场景需要先创建一次
        if "name重复" in description:
            # 先创建一次
            admin_api.edit(
                title = "预创建标题",
                name = test_name,
                editor = "markdown",
                content = "预创建内容",
                summary = "预创建摘要",
                h_role = 0,
                price = "0.00",  # 建议字符串
                h_content = '<p>3333</p>',  # 修复 HTML 标签闭合
                state = 1,
                category_id = 1,
                tagsinput = "eqweqw",
                thumbnail = '/static/img/thumbnail.jpg',
                author = "管理员",
                vc = 0,
                publish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            # 确保已存在
            pre_check = admin_api.get_article(title = test_title)
            assert pre_check['total'] >= 1, "预创建失败"

    with allure.step(f"执行新增：{description}"):
        resp = admin_api.edit(
            title = test_title,
            name = test_name,
            editor = "markdown",
            content = content,
            summary = "测试摘要",
            h_role = 0,
            price = "0.00",  # 建议字符串
            h_content = '<p>测试内容</p>',  # 修复 HTML 标签闭合
            state = 1,
            category_id = category_id,
            tagsinput = "test",
            thumbnail='/static/img/thumbnail.jpg',
            author="管理员",
            vc = 0,
            publish_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        # 可选：附加响应片段用于调试
        if resp.headers.get('content-type').startswith('text/html'):
            snippet = resp.text()
            allure.attach(snippet, "响应HTML片段", allure.attachment_type.HTML)

    with allure.step("验证文章未被创建"):
        # 核心断言：查不到这篇文章
        result = admin_api.get_article(title = test_title)
        assert result['total'] == 0, f"异常场景下文章被创建！标题：{test_title}"

        # 额外：如果是 'name重复'，确保只有一篇（预创建的）
        if "name重复" in description:
            name_check = admin_api.get_article(title = test_name)
            assert name_check['total'] == 1, "name重复场景应只保留创建的文章"

    allure.attach("自动化异常用例通过", "结果", allure.attachment_type.TEXT)

@allure.title("文章管理-03：新增-修改-删除端对端流程")
@allure.description("验证文章核心流程的连贯性：创建-编辑-删除")
@allure.severity(allure.severity_level.CRITICAL)
def test_article_add_edit_remove(admin_api):
    """端到端流程测试：新增 → 修改 → 删除"""

    #生成唯一标识
    unique = str(int(time.time()) * 1000)
    original_title = f"测试流程_原始_{unique}"
    original_name = f"flow_test_original_{unique}"
    updated_title = f"流程测试_修改后_{unique}"

    # 新增文章
    with allure.step("Step1:新增文章"):
        admin_api.edit(
            title = original_title,
            name = original_name,
            editor = "markdown",
            content = "原始内容",
            summary = "原始摘要",
            h_role = 0,
            price = "0.00",  # 建议字符串
            h_content = '<p>原始HTML</p>',  # 修复 HTML 标签闭合
            state = 1,
            category_id = 1,
            tagsinput = "flow:test",
            thumbnail = '/static/img/thumbnail.jpg',
            author = "管理员",
            vc = 0,
            publish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        result = admin_api.get_article(title = original_title)
        assert result['total'] >= 1, "新增文章未被找到"
        article_id = result["rows"][0]['id']
        allure.attach(str(article_id), "新增文章ID", allure.attachment_type.TEXT)

    with allure.step("Step2:修改文章"):
        admin_api.edit(
            id = article_id, # 传入id标识指定文章进行修改
            title = updated_title,
            name = original_name,
            editor = "markdown",
            content = "修改后的内容",
            summary = "修改后的摘要",
            h_role = 0,
            price = "0.00",  # 建议字符串
            h_content = '<p>修改后的HTML</p>',  # 修复 HTML 标签闭合
            state = 1,
            category_id = 1,
            tagsinput = "test",
            thumbnail = '/static/img/thumbnail.jpg',
            author = "管理员",
            vc = 0,
            publish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        # 验证修改生效：查新标题
        updated_result = admin_api.get_article(title = updated_title)
        assert updated_result['total'] >= 1, "修改文章后的标题未找到"
        assert updated_result["rows"][0]["id"] == article_id, "文章ID不应改变"

    with allure.step("Step3:删除文章"):
        del_resp = admin_api.remove(article_id)
        # 不断言 del_resp（可能返回 200 HTML），直接验证结果
        # 验证删除：查新标题和旧标题都不存在
        check_new = admin_api.get_article(title = original_title)
        check_old = admin_api.get_article(title = updated_title)

        assert check_new["total"] == 0, "删除后仍能找到新标题的文章"
        assert check_old["total"] == 0, "删除后仍能找到旧标题的文章"

    allure.attach("端对端测试通过", "结果", allure.attachment_type.TEXT)

@allure.title("文章管理-04：用户无权新增文章")
@allure.description("验证普通用户无法调用新增接口")
@allure.severity(allure.severity_level.CRITICAL)
def test_article_edit_without_permission(normal_api):
    """权限测试：用普通用户 session 尝试越权调用 admin 接口"""
    title = "普通用户越权"
    with allure.step("普通用户调用管理员接口"):
        resp = normal_api.edit(
            title=title,
            name="333333",
            editor='markdown',
            content='1111',
            summary='2222',
            h_role=0,
            price="0.00",  # 建议字符串
            h_content='<p>3333</p>',  # 修复 HTML 标签闭合
            state=1,
            category_id=1,
            tagsinput='4444',
            thumbnail='/static/img/thumbnail.jpg',
            author="管理员",
            vc=0,
            publish_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        # === 记录请求与响应到 Allure 报告 ===
        allure.attach(
            f"POST /admin/cms/article/edit\nStatus: {resp.status_code}\nContent-Type: {resp.headers.get('Content-Type', 'unknown')}",
            name = "请求响应和摘要",
            attachment_type = allure.attachment_type.TEXT
        )

        allure.attach(
            resp.text,
            name = "响应内容片段",
            attachment_type = allure.attachment_type.TEXT
        )

        # === 断言逻辑 ===
        if resp.status_code == 200:
            # 检查是否返回了登录页面（说明未授权）
            assert "<title>登录</title>" in resp.text, "应返回登录页，但未检测到"
            allure.attach("权限拦截成功：返回登录页面", name = "断言结果", attachment_type = allure.attachment_type.TEXT)
        elif resp.status_code in (302, 401, 403):
            allure.attach(f"拦截成功，状态码：{resp.status_code}", name = "断言结果", attachment_type = allure.attachment_type.TEXT)
        else:
            pytest.fail(f"意外状态码：{resp.status_code}")

@allure.title("文章管理-05：修改不存在的文章ID")
@allure.description("验证传入不存在的ID时，接口返回友好错误")
@allure.severity(allure.severity_level.NORMAL)
def test_edit_nonexistent_id(admin_api):
    fake_id = 9999

    with allure.step(f"尝试编辑不存在的ID：{fake_id}"):
        resp = admin_api.edit(
            id = fake_id,
            title = "非法标题",
            name = "fake_name",
            editor = "markdown",
            content = "内容",
            summary = "摘要",
            h_role = 0,
            price = "0.00",
            h_content = "<p>内容</p>",
            state = 1,
            category_id = 1,
            tagsinput = "test",
            thumbnail = '/static/img/thumbnail.jpg',
            author = "管理员",
            vc=0,
            publish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        if resp.headers.get('content-type', '').startswith('application/json'):
            json_resp = resp.json()
            assert json_resp.get('code') != 0, "应返回错误码"
            assert "不存在" in json_resp.get('msg', '') or "操作失败" in json_resp.get('msg', ''), "错误信息应提示文章不存在或拦截操作"
        else:
            assert resp.status_code in (404, 500), f"意外状态码：{resp.status_code}"
            assert "文章不存在" in resp.text or "not found" in resp.text.lower()

    allure.attach("修改不存在ID拦截成功", "结果", allure.attachment_type.TEXT)


@allure.title("文章管理-06：编辑后列表/搜索同步验证")
@allure.description("验证编辑文章后，列表和搜索接口能立即反映更新")
@allure.severity(allure.severity_level.NORMAL)
def test_edit_data_sync(admin_api):
    """编辑后验证数据同步到列表接口"""
    unique = str(int(time.time()))
    original_title = f"同步前{unique}"
    update_title = f"同步后{unique}"

    admin_api.edit(
        title = original_title,
        name = f"sync_{unique}",
        editor = "markdown",
        content = "内容",
        summary = "摘要",
        h_role = 0,
        price = "0.00",
        h_content = "<p>内容</p>",
        state = 1,
        category_id = 1,
        tagsinput = "test",
        thumbnail = '/static/img/thumbnail.jpg',
        author = "管理员",
        vc = 0,
        publish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    result = admin_api.get_article(title = original_title)
    article_id = result["rows"][0]["id"]

    admin_api.edit(
        id = article_id,
        title = update_title,
        name = f"sync_{unique}",
        editor = "markdown",
        content = "内容",
        summary = "摘要",
        h_role = 0,
        price = "0.00",
        h_content = "<p>内容</p>",
        state = 1,
        category_id = 1,
        tagsinput = "test",
        thumbnail = '/static/img/thumbnail.jpg',
        author = "管理员",
        vc = 0,
        publish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    old_check = admin_api.get_article(title = original_title)
    new_check = admin_api.get_article(title = update_title)

    assert old_check['total'] == 0, "旧标题仍能找到"
    assert new_check['total'] >= 1, "新标题未同步"
    assert new_check['rows'][0]['id'] == article_id, "ID不一致"

    allure.attach("数据同步验证通过", "结果", allure.attachment_type.TEXT)