import pytest
from my_utils.login import APIClient
from api.article_api import ArticleApi
import time
from datetime import datetime
import requests

BASE_URL = "http://localhost:5000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123456"
NORMAL_USERNAME = "1903358284"
NORMAL_PASSWORD = "1903358284"

# ================= 基础登录 fixtures =================

@pytest.fixture(scope = "function")
def admin_api():
    """
    返回一个已登录的 ArticleAPI 实例（管理员权限）
    测试结束后自动清理本次创建的测试文章
    """
    # 登录
    client = APIClient(BASE_URL)
    try:
        client.login(ADMIN_USERNAME, ADMIN_PASSWORD)
    except Exception as e:
        client.close()
        pytest.fail(f"管理员登录失败：{e}")

    # 初始化 ArticleAPI（传入 session）
    api = ArticleApi(base_url = BASE_URL, session = client.session)

    # 提供给测试用例
    yield api

    # 测试结束后关闭会话
    client.close()

@pytest.fixture(scope = "function")
def normal_api():
    client = APIClient(BASE_URL)
    try:
        client.login(NORMAL_USERNAME, NORMAL_PASSWORD, login_path = "/login")
    except Exception as e:
        pytest.fail(f"普通用户登录失败：{e}")

    api = ArticleApi(base_url=BASE_URL, session=client.session)

    yield api

    client.close()

# ================= 业务数据工厂 fixtures =================

@pytest.fixture
def create_test_articles(admin_api):
    """
    【数据工厂】
    返回格式：[(id1, title1), (id2, title2), ...]
    """
    created_data = []  # 记录所有 (id, title) 用于 teardown

    def _create(count = 1, state = 1, prefix = "AutoDel"):
        current_batch = []
        for i in range(count):
            # 生成唯一标识，防止并发冲突

            unique = str(int(time.time() *1000) + i)
            title = f"{prefix}_{state}_{unique}"

            try:
                # 调用新增接口
                admin_api.edit(
                    title = title,
                    name = f"name_{unique}",
                    editor = "markdown",
                    content = "测试内容",
                    summary = "摘要",
                    h_role = 0,
                    price = "0.00",
                    h_content = "<p>HTML</p>",
                    state = state,
                    category_id = 1,
                    tagsinput = "test",
                    thumbnail = "/static/img/thumb.jpg",
                    author = "管理员",
                    vc = 0,
                    publish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )

                # 获取刚创建的 ID (通过标题反查)
                res = admin_api.get_article(title = title)

                if res.get("total", 0) > 0 and len(res.get("rows", [])) > 0:
                    aid = res["rows"][0]["id"]
                    # 【关键修改】构建元组 (id, title)
                    item = (aid, title)
                    current_batch.append(item)  # 加入当前批次返回
                    created_data.append(item)  # 加入全局清理列表
                else:
                    pytest.fail(f"文章创建成功但无法查询到ID:{title}")

            except Exception as e:
                pytest.fail(f"创建测试文章失败({title}:{str(e)})")

        return current_batch
    yield _create

    # Teardown
    # 测试结束后，无论成功失败，都尝试删除创建的数据

    if created_data:
        print(f"\n[Teardown] 正在清理 {len(created_data)}篇测试文章")
        # 提取所有 ID (元组的第 0 个元素)
        ids_to_delete = [item[0] for item in created_data]
        try:
            # 批量删除，提高效率
            admin_api.remove(ids=ids_to_delete)
            print(f"[Teardown]清理完成")
        except Exception as e:
            # 记录警告但不中断测试报告（因为主测试可能已经失败了）
            print(f"[Teardown Warning] 清理部分数据失败：{str(e)}")