import requests

class ArticleApi:
    def __init__(self, base_url, session):
        """
        :param session: requests.Session() 实例（已登录）
        :param base_url: 基础 URL，如 "http://127.0.0.1:5000"
        """
        self.session = session
        self.base_url = base_url

    def edit(self, title, name, editor, content, summary, h_role, price, h_content, state, category_id, tagsinput, thumbnail, author, vc, publish_time, id = None):
        """新增文章"""
        url = f"{self.base_url}/admin/cms/article/edit"
        payload = {
            "title": title,
            "name": name,
            "editor": editor,
            "content": content,
            "summary": summary,
            "h_role": h_role,
            "price": price,
            "h_content": h_content,
            "state": state,
            "category_id": category_id,
            "tagsinput": tagsinput,
            "thumbnail": thumbnail,
            "author": author,
            "vc": vc,
            "publish_time": publish_time
        }

        if id is not None:
            payload["id"] = id

        return self.session.post(url, data = payload)

    def remove(self, ids):
        url = f"{self.base_url}/admin/cms/article/remove"
        payload = {"ids": ids}
        return self.session.post(url, data = payload)

    def get_article(self, pageSize = 10, pageNum = 1, isAsc = "asc", category_id = None, title = None, state = None, publish_time_start = None, publish_time_end = None):
        url = f"{self.base_url}/admin/cms/article/list"
        payload = {
            "pageSize": pageSize,
            "pageNum": pageNum,
            "isAsc": isAsc
        }
        if title is not None:
            payload["title"] = title
        if category_id is not None:
            payload["category_id"] = category_id
        if state is not None:
            payload["state"] = state
        if publish_time_start is not None:
            payload["publish_time_start"] = publish_time_start
        if publish_time_end is not None:
            payload["publish_time_end"] = publish_time_end

        resp = self.session.post(url, data = payload)

        print(">>> 请求 URL:", url)
        print(">>> 响应状态码:", resp.status_code)
        print(">>> 原始响应内容（前300字符）:")
        print(repr(resp.text))
        print(">>> Content-Type:", resp.headers.get('content-type'))

        resp.raise_for_status() # HTTP 响应状态码表示出错时自动抛出异常

        data = resp.json()
        if not isinstance(data, dict):
            raise Exception("文章列表接口返回非 JSON 对象")
        code = data.get("code")
        if code != 0:
            msg = data.get("msg", "未知错误")
            raise Exception(f"文章列表接口失败 (code={code}): {msg}")

        return data