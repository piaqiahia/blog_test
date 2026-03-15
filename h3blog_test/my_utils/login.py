import requests

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def login(self, username, password, login_path="/admin/login"):
        """
        登录系统，自动保存 Session Cookie
        """
        # Flask 默认登录通常是 x-www-form-urlencoded
        CAPTCHAR = "0000"  # 0000直接pass 万用验证码

        login_url = f"{self.base_url}{login_path}"

        if login_path == "/admin/login":
            payload = {
                'login-username': username,
                'login-password': password,
                'login-captcha': CAPTCHAR
            }
        elif login_path == "/login":
            payload = {
                'username': username,
                'password': password
            }
        else:
            raise ValueError(f"不支持的登录路径：{login_path}")

        resp = self.session.post(login_url, data = payload)
        resp.raise_for_status()

        if resp.status_code == 200:
            # 重定向说明登录成功（Flask-Login 默认行为）
            return True
        elif "登录失败" in resp.text or 'Invalid' in resp.text:
            raise Exception("用户名或密码错误")
        else:
            # 尝试访问一个需登录的页面验证
            test_resp = self.session.get(f"{self.base_url}/admin/")
            if test_resp.status_code == 200:
                return True
            else:
                raise Exception("登录失败")

    def get_admin_page(self):
        """获取 admin 首页 HTML 内容"""
        url = f"{self.base_url}/admin/"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.text

    def get(self, path, **kwargs):
        url = f"{self.base_url}{path}"
        return self.session.get(url, **kwargs) # 这里的get post是requests.Session的get/post 用来发送请求

    def post(self, path, **kwargs):
        url = f"{self.base_url}{path}"
        return self.session.post(url, **kwargs)

    def close(self):
        self.session.close()