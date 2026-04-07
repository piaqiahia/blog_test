import sys
import os
import time

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("Project root:", project_root)  # 调试用，确认路径正确

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from my_utils.login import APIClient
from article_api import ArticleApi

def articleapi_test():
    client = APIClient("http://127.0.0.1:5000")
    title_name = f"{time.time()}test"
    try:
        # 登录
        client.login("admin", "123456")
        print("登录成功")

        # 初始化api
        api = ArticleApi("http://127.0.0.1:5000", client.session)

        # 获取列表
        data = api.get_article(title = title_name)
        print(f"列表获取成功，共{data['total']}条")

        # 新增文章
        resp = api.edit(
            title = f"{title_name}",
            name = f"{title_name}",
            editor = 'markdown',
            content = '1111',
            summary = '2222',
            h_role = 0,
            price = 0.0,
            h_content = '<p>3333<p>',
            state = 1,
            category_id = 1,
            tagsinput = '4444',
            thumbnail = '/static/img/thumbnail.jpg',
            author = "管理员",
            vc = 0,
            publish_time = "2026-03-05 12:00:30"
        )
        print("创建文章成功")

        new_data = api.get_article(title = f"{title_name}")
        if new_data["total"] > 0:
            article_id = new_data["rows"][0]["id"]
            print(f"找到新文章，ID:{article_id}")

            # 删除文章
            del_resp = api.remove(article_id)
            new_data = api.get_article(title = f"{title_name}")
            if new_data["total"] == 0:
                print("文章删除成功")
            else:
                print("删除失败", del_resp.text)
        else:
            print("未找到新文章，跳过删除")

    except Exception as e:
        print(f"测试失败：{e}")
    finally:
        client.close()

if __name__ == "__main__":
    articleapi_test()
