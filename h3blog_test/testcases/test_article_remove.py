import pytest
import allure
import time

@allure.feature("文章管理 - 删除操作")
class TestArticleRemove:

    # ==========================================
    # 【关键】辅助方法：复现 Title 生成逻辑
    # ==========================================
    def _generate_expected_titles(self, count, state, prefix, start_time_ms):
        """
        根据 create_test_articles 的逻辑，反推出创建的标题列表。
        逻辑：f"{prefix}_{state}_{unique}"，其中 unique = start_time_ms + i
        """
        titles = []
        for i in range(count):
            unique = str(start_time_ms + i)
            title = f"{prefix}_{state}_{unique}"
            titles.append(title)
        return titles

    # ---------------------------------------------------------
    # 场景 1: 特殊状态文章删除 (已发布 vs 已下架)
    # ---------------------------------------------------------
    @pytest.mark.parametrize(
        "state, state_desc",
        [
            (1, "已发布"),
            (0, "草稿")
        ],
        ids = ["Published", "Unpublished"]
    )
    @allure.title("状态测试: 删除{state_desc}的文章")
    def test_remove_by_state(self, admin_api, create_test_articles, state, state_desc):
        """
        验证是否能删除不同状态的文章（特别是已下架文章，常出现逻辑漏洞）。
        """
        prefix = f"State_{state_desc}"
        count = 1

        # 创建
        with allure.step(f"创建一篇{state_desc}的文章"):
            start_time_ms = int(time.time() * 1000)
            ids = create_test_articles(count = count, state = state, prefix = prefix)
            assert len(ids) == count
            target_id = ids[0]

            # 调用类内的辅助方法生成预期标题
            expected_titles = self._generate_expected_titles(count, state, prefix, start_time_ms)

        # 执行删除
        with allure.step(f"删除{state_desc}文章ID:{target_id}"):
            resp = admin_api.remove(ids = target_id)

        # 查库验证
        with allure.step("验证数据已移除"):
            res = admin_api.get_article(title = expected_titles)
            assert res.get("total") == 0, f"删除{state_desc}文章后，文章仍存在(Total = {res.get('total')})"


    # ---------------------------------------------------------
    # 场景 2: 权限测试 + 验证数据未丢失
    # ---------------------------------------------------------
    @pytest.mark.parametrize(
        "api_fixture, role_name, should_deleted",
        [
            ("admin_api", "管理员", True),
            ("normal_api", "普通用户", False)
        ],
        ids=["Admin_Allow", "User_Forbid"]  # 这个 ids 很重要，决定了测试用例的名字
    )
    @allure.title("权限测试：{role_name}尝试删除")
    def test_remove_permission_strict(self, request, api_fixture, role_name, should_deleted, create_test_articles):

        # ---------------------------------------------------------
        # 强制在控制台打印日志
        # ---------------------------------------------------------
        print("\n" + "=" * 60)
        print(f"开始执行测试：[{role_name}] (Fixture: {api_fixture})")
        print(f"   预期结果：{'允许删除' if should_deleted else '禁止删除'}")
        print("=" * 60)

        current_api = request.getfixturevalue(api_fixture)
        admin_api = request.getfixturevalue("admin_api")

        # ---------------------------------------------------------
        # 【关键修改 2】把身份信息写入 Allure 报告（即使测试失败也能看到）
        # ---------------------------------------------------------
        allure.attach(
            f"当前测试角色：{role_name}\n"
            f"使用 Fixture: {api_fixture}\n"
            f"Session Cookie: {current_api.session.cookies.get_dict()}",
            name="测试身份确认",
            attachment_type=allure.attachment_type.TEXT
        )

        prefix = f"Perm_{role_name}"

        # 1. 造数据
        with allure.step("管理员创建测试数据"):
            data_list = create_test_articles(count=1, state=1, prefix=prefix)
            target_id, target_title = data_list[0]
            allure.attach(f"创建成功 -> ID:{target_id}, title:{target_title}", "数据信息")

            # 2. 删除操作
            with allure.step(f"[{role_name}] 尝试删除 ID: {target_id}"):
                print(f"正在调用 remove 接口，发送者：{role_name}")

                resp = current_api.remove(ids=[target_id])

                # 打印响应详情
                print(f"删除接口返回状态码：{resp.status_code}")

                # 尝试解析 JSON (如果是 HTML 说明被重定向到登录页了)
                try:
                    resp_json = resp.json()
                    print(f"删除接口返回 JSON: {resp_json}")

                    # 检查业务码
                    if resp_json.get('code') != 0:
                        print(f"业务层拦截！Code: {resp_json.get('code')}, Msg: {resp_json.get('msg')}")
                    else:
                        print(f"业务层返回成功 (code=0)，需依赖数据库验证确认是否真删了。")

                except Exception:
                    # 如果不是 JSON，可能是 HTML (登录页) 或纯文本
                    print(f"响应不是 JSON (可能是 HTML 登录页或错误页): {resp.text[:200]}...")
                    if "登录" in resp.text or "signin" in resp.text:
                        print(f"发现未登录！普通用户 Session 丢失或未生效。")

        # 3. 验证结果
        with allure.step(f"验证 [{role_name}] 的删除结果"):
            res = admin_api.get_article(title=target_title)
            final_total = res.get('total', -1)

            print(f"数据库查询结果：剩余 {final_total} 条")

            if should_deleted:
                # 管理员应该删成功 (剩 0 条)
                assert final_total == 0, (
                    f"[权限漏洞] {role_name} 应该删除成功，但数据还在！\n"
                    f"剩余数量：{final_total}"
                )
            else:
                # 普通用户应该删失败 (剩 1 条)
                assert final_total >= 1, (
                    f"[权限漏洞] {role_name} 不应删除成功，但数据没了！\n"
                    f"剩余数量：{final_total}"
                )

        print(f"[{role_name}] 测试通过！\n")



    # ---------------------------------------------------------
    # 场景 4: 边界与混合 ID 测试 (新增)
    # ---------------------------------------------------------
    @pytest.mark.parametrize(
        "test_case, ids_input, description",
        [
            ("non_existent", [99999], "删除不存在的ID"),
            ("negative", [-1], "删除负数ID"),
            ("mixed", None, "混合真实ID与不真实ID")
        ],
        ids = ["NonExistent", "Negative", "Mixed"]
    )
    @allure.title("边界测试：{description}")
    def test_remove_edge_cases(self, admin_api, create_test_articles, test_case, ids_input, description):
        """
        验证删除接口对异常 ID 或混合 ID 的处理，确保不报错、不误删。
        因为 -1 和 99999 系统中不存在这样的ID 因此无需为这两个用例创建文章
        """

        real_ids = []
        real_titles = []

        # 如果是混合测试，先创建真实数据
        if test_case == "mixed":
            with allure.step("创建两篇真实文章用于混合测试"):
                data_list = create_test_articles(count = 2, state = 1, prefix = "Edge_Mixed")
                real_ids = [item[0] for item in data_list]
                real_titles = [item[1] for item in data_list]
                ids_input = real_ids + [88888888] # 真实ID + 假ID
                allure.attach(f"混合ID：{ids_input}", "输入数据")

        # 删除
        with allure.step(f"执行删除：{description}"):
            try:
                resp = admin_api.remove(ids = ids_input)
                # 只要不报 500 错误，通常视为系统健壮性合格
                if resp.status_code == 500:
                    pytest.fail(f"服务器因输入{description}崩溃(500 Error)")
            except Exception as e:
                pytest.fail(f"客户端抛出异常：{str(e)}")

        # 验证：如果是混合测试，确认真实数据被删了；如果是纯假数据，确保没误删其他东西
        with allure.step("验证数据"):
            if test_case == "mixed":
                # 真实的那部分不应该被删掉
                i = 0
                for title in real_titles:
                    i += 1
                    res = admin_api.get_article(title = title)
                    print(f"这是第{i}个")
                    assert res.get('total') == 0, f"混合删除中，真实文章{title}未被删除"
                allure.attach("混合测试通过：真实数据被删除，假数据被忽略", "验证结果")
            else:
                # 纯假数据测试：随便查一个系统里肯定有的东西（比如分类），确保没崩导致库乱了
                # 这里简单认为只要没报 500 就算过
                allure.attach("异常输入测试通过：未引发服务器崩溃", "验证结果")
    # ---------------------------------------------------------
    # 场景 4: 安全与异常格式测试 (新增)
    # ---------------------------------------------------------
    @pytest.mark.security
    @pytest.mark.parametrize(
        "bad_input, desc",
        [
            ("", "空字符串"),
            ("adb,def", "非数字字符"),
            ("1;DROP TABLE articles", "SQL尝试注入"),
            (" ", "纯空格")
        ],
        ids = ["Empty", "NonNumeric", "SQL_Injection", "WhiteSpace"]
    )
    @allure.title("安全测试：输入{desc}")
    def test_remove_security_inputs(self, admin_api, bad_input, desc):
        """
        直接调用底层 Session 发送数据，测试后端解析器的健壮性和安全性。
        """

        url = f"{admin_api.base_url}/admin/cms/article/remove"

        with allure.step(f"发送恶意数据：{desc}"):
            # 直接 POST 表单数据，绕过封装层的参数校验
            resp = admin_api.session.post(url, data = {"ids", bad_input})

            allure.attach(f"响应状态码：{resp.status_code}", "状态码")
            allure.attach(resp.text[:300], "响应内容片段", allure.attachment_type.TEXT)

            # 核心断言：服务器绝不能因为畸形输入而崩溃 (500)
            assert resp.status_code != 500, f"服务器因输入'{desc}'崩溃（500 Error），存在安全隐患"

            # 如果返回 200，检查是否返回了友好的错误提示而不是堆栈信息
            if resp.status_code == 200 and "Traceback" in resp.text:
                pytest.fail(f"虽然状态码200，但响应中包含python堆栈信息，存在信息泄露风险")


    # ---------------------------------------------------------
    # 场景 5: 正向删除 (单篇/批量/大量) - 参数化 ID 数量
    # ---------------------------------------------------------
    @pytest.mark.parametrize(
        "count, scenario_name",
        [
            (1, "单篇删除"),
            (3, "小批量删除3"),
            (10, "中批量删除 10"),
            (50, "大批量删除 50（性能边界试探）")
        ],
        ids = ["Single", "Batch_Small", "Batch_Medium", "Batch_Large"]
    )
    @allure.title("正向测试：{scenario_name}")
    def test_remove_positive_batch(self, admin_api, create_test_articles, count, scenario_name):
        """
        验证不同数量级的文章删除功能是否正常，并逐一确认数据消失。
        """

        prefix = f"Pos_{scenario_name}"

        # 造数据
        with allure.step(f"创建{count}篇测试文章{scenario_name}"):
            start_time_ms = int(time.time() * 1000)
            data_list = create_test_articles(count = count, state = 1, prefix = prefix)

            target_ids = [item[0] for item in data_list]
            target_titles = [item[1] for item in data_list]

            assert len(data_list) == count, "创建数量与预期不符"
            allure.attach(f"创建 IDs:{target_ids[:5]}{'...' if len(target_ids) > 5 else ''}", "创建数据列表")
            allure.attach(f"创建 Titles:{target_titles[:2]}...", "部分标题示例")

        # 开始删除
        with allure.step(f"批量删除{count}篇文章"):
            start_op = time.time()
            ids_str = ",".join(map(str, target_ids))
            resp = admin_api.remove(ids=ids_str)
            duration = time.time() - start_op

            allure.attach(f"耗时：{duration:.4f}秒", "性能数据")

            # 检查响应
            try:
                resp_json = resp.json()
            except Exception as e:
                if resp.status_code != 200:
                    pytest.fail(f"删除操作HTTP失败：{resp.status_code}")

        # 验证结果
        with allure.step("验证所有数据已经删除"):
            missing_count = 0
            failed_titles = []

            # 遍历fixture返回的真实标题列表
            for aid, title in data_list:
                res = admin_api.get_article(title = title)
                if res.get("total", 0) == 0:
                    missing_count += 1
                else:
                    failed_titles.append(title)

            # 断言
            assert missing_count == count, (
                f"批量删除后仍有数据残余！\n",
                f"预期删除：{count}篇\n",
                f"实际删除：{count - missing_count}篇\n",
                f"标题残留：{failed_titles}"
            )

            # 性能断言
            if count >= 30:
                assert duration < 3.0, f"大批量删除({count}条)，耗时过长：{duration:.2f}s"