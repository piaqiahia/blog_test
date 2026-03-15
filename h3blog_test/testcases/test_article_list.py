import pytest
import allure
import requests
import time

@allure.feature("文章接口-分页功能")
class TestPagination():

    @pytest.mark.parametrize(
        "pageNum, pageSize, desc, expect_empty",
        [
            (1, 10, "首页_默认页宽", False),
            (2, 10, "第二页_默认页宽", False),
            (1, 5, "首页_小页宽", False),
            (1, 50, "首页_大页宽", False),
            (9999, 10, "页码越界_超大值", True),
            (0, 10, "页码越界_零值", None),
            (-1, 10, "页码越界_负值", None),
            (1, 0, "页宽越界_零值", None),
            (1, -5, "页宽越界_负值", None),
        ],
        ids = ["P01", "P02", "P03_Size5", "P03_Size50", "P05_Overflow", "P06_Zero", "P06_Neg", "P07_Zero", "P07_Neg"]
    )
    @allure.title("分页场景：{desc}")
    def test_pagination_scenario(self, admin_api, pageNum, pageSize, desc, expect_empty):
        with allure.step(f"发起请求，pageSize = {pageSize}, pageNum = {pageNum}"):
            resp = admin_api.get_article(pageNum = pageNum, pageSize = pageSize)

        with allure.step("验证响应"):
            # 基础结构检查
            assert "code" in resp, "缺少data字段"
            assert "rows" in resp, "缺少rows字段"
            assert "total" in resp, "缺少total字段"

            rows = resp["rows"]

            # 业务逻辑断言
            if expect_empty:
                assert len(rows) == 0, f"页面越界（9999）应返回空列表，实际返回{len(rows)}条数据"
            elif expect_empty is False:
                # 正常情况：返回数量不应超过 pageSize
                assert len(rows) <= pageSize, f"返回数量：{len(rows)}，超过限制{pageSize}"
                # 验证数据不重复 (检查 ID)
                ids = [r['id'] for r in rows]
                assert len(rows) == len(set(ids)), "分页数据存在重复ID"

@allure.feature("文章接口 - 搜索功能")
class TestSearch():
    @allure.title("S01:精确搜索唯一标题")
    def test_search_extra_match(self, admin_api, create_test_articles):
        unique = str(time.time())
        with allure.step(f"搜索唯一标题：{unique}"):
            resp = admin_api.get_article(title = unique)

            for row in resp["rows"]:
                assert unique in row["title"], f"精确搜索失败，返回了不匹配的数据：{row['title']}"

    @pytest.mark.parametrize(
        "keyword, should_be_empty, desc",
        [
            ("测试", False, "S02:模糊搜索常用词"),
            ("XYZ_NOT_EXIST_9999_ABC", True, "S03:搜索无结果"),
            ("<script>alert('1')</script>", None, "S04:特殊字符安全")
        ],
        ids = ["S02_Fuzzy", "S03_Empty", "S04_SpecialChar"]
    )
    @allure.title("搜索场景：{desc}")
    def test_search_keywords(self, admin_api, keyword, should_be_empty, desc):
        with allure.step(f"搜索关键词：{keyword}"):
            resp = admin_api.get_article(title = keyword)

        with allure.step("验证结果"):
            rows = resp["rows"]

            if should_be_empty:
                assert len(rows) == 0, f"搜索不存在的关键词'{keyword}'应该返回空列表"
            else:
                # 如果有数据，验证内容匹配
                if len(rows) > 0:
                    for row in rows:
                        assert keyword in row["title"], f"模糊搜索未匹配：{row[title]}"
