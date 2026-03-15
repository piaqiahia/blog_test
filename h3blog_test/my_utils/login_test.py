from login import APIClient

def create_article_test():
    client = APIClient("http://127.0.0.1:5000")

    try:
        # 登录
        success = client.login("admin", "123456", "jksi")
        print(success)
        if success:
            print("登录成功")
            admin_html = client.get_admin_page()
            print(admin_html)
        else:
            print("❌ 登录失败（未抛异常但返回 False）")
    except Exception as e:
        print(f"登陆失败：{e}")
    finally:
        client.close()

create_article_test()