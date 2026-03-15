import sys
import os
import subprocess
import shutil
from my_utils.login import APIClient
import time
import socket

BASE_URL = "http://localhost:5000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123456"
TEST_USERNAME = "1903358284"
TEST_PASSWORD = "1903358284"
TEST_EMAIL = "0000@a.a"  # 特殊邮箱，触发后门
TEST_YZM = "0000"  # 特殊验证码，触发后门

def main():
    # 当前脚本在 h3blog_test 目录下
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 测试用例目录
    test_dir = os.path.join(current_dir, "testcases")

    # 报告路径
    html_report_path = os.path.join(current_dir, "reports", "report.html")
    allure_results_path = os.path.join(current_dir, "allure-results")
    allure_report_path = os.path.join(current_dir, "allure-report")

    # 确保目录存在
    os.makedirs(os.path.dirname(html_report_path), exist_ok=True)

    # ========== 等待 Web 服务就绪（10分钟超时）==========
    print("=" * 60)
    print("# Web 服务就绪 (最多等待 10 分钟)...")
    print("=" * 60)

    host = "web"
    port = 5000
    timeout = 900  # 10分钟 = 600秒
    check_interval = 2  # 每2秒检查一次

    start_time = time.time()
    service_ready = False

    while time.time() - start_time < timeout:
        try:
            # 尝试建立 TCP 连接
            with socket.create_connection((host, port), timeout=5):
                print(f"\nWeb 服务 {host}:{port} 已就绪！")
                service_ready = True
                break
        except (socket.error, ConnectionRefusedError, OSError):
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed

            # 每10秒打印一次进度
            if elapsed % 10 == 0:
                print(f"等待中... ({elapsed}s/{timeout}s, 剩余 {remaining}s)")

            time.sleep(check_interval)

    # 检查是否超时
    if not service_ready:
        print(f"\n错误：Web 服务 {host}:{port} 在 {timeout} 秒内未就绪")
        print("请检查容器日志或增加超时时间")
        sys.exit(1)

    print("=" * 60)

    # 【修改】安全地处理 allure-results 目录
    if os.path.exists(allure_results_path):
        try:
            shutil.rmtree(allure_results_path)
        except OSError as e:
            print(f"警告: 无法删除旧的 allure-results 目录: {e}")
            print("将尝试清空内容...")
            for item in os.listdir(allure_results_path):
                item_path = os.path.join(allure_results_path, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    else:
                        shutil.rmtree(item_path)
                except:
                    pass

    # 确保目录存在
    os.makedirs(allure_results_path, exist_ok=True)
    print(f"Allure 结果目录: {allure_results_path}")

    client = APIClient(BASE_URL)
    pre_check_success = False

    client = APIClient(BASE_URL)

    # 标志变量，标记前置操作是否成功
    pre_check_success = False

    try:
        # ===== 1. 注册普通用户（使用后门，不发送验证码）=====
        print("正在注册普通用户（使用后门模式）...")
        regist_url = "/regist"
        regist_payload = {
            'username': TEST_USERNAME,
            'password': TEST_PASSWORD,
            'email': TEST_EMAIL,
            'yzm': TEST_YZM
        }

        resp = client.session.post(f"{BASE_URL}{regist_url}", data=regist_payload)

        print(f"状态码: {resp.status_code}")
        print(f"响应头: {dict(resp.headers)}")
        print(f"响应内容（前500字符）: {resp.text[:500]}")
        print("=" * 50)

        if resp.status_code == 200:
            try:
                result = resp.json()
                if result.get('code') == 0:
                    print(f"用户注册成功！用户名: {TEST_USERNAME}")
                    print(f"邮箱: {TEST_EMAIL}")
                    print(f"验证码: {TEST_YZM}")
                else:
                    print(f"注册失败: {result.get('msg')}")
                    print(f"完整响应: {resp.text}")
            except Exception as e:
                print(f"解析JSON失败: {e}")
                print(f"响应内容: {resp.text}")
        else:
            print(f"注册请求返回状态码: {resp.status_code}")
            print(f"响应内容: {resp.text}")

        # ===== 2. 登录系统 =====
        print("\n正在登录...")
        client.login(ADMIN_USERNAME, ADMIN_PASSWORD)
        print("登录成功！")

        # ===== 3. 切换主题 =====
        theme_url = "/admin/cms/theme/activate?id=1"
        print(f"\n正在切换主题: {theme_url}")
        response = client.get(theme_url)

        # 检查响应状态
        if response.status_code == 200:
            print(f"主题切换成功！状态码: {response.status_code}")
            pre_check_success = True  # 标记成功
        else:
            print(f"主题切换返回非200状态码: {response.status_code}")
            # 即使状态码不是200，也继续执行测试
            pre_check_success = True

    except Exception as e:
        print(f"操作失败：{e}")
        import traceback
        traceback.print_exc()
        pre_check_success = False  # 标记失败
    finally:
        client.close()

    # 如果前置操作失败，直接退出
    if not pre_check_success:
        print("\n前置操作失败，终止测试执行")
        sys.exit(1)

    # 构造 pytest 命令
    cmd = [
        sys.executable,
        "-m", "pytest",
        test_dir,
        "-v",
        "-s",
        f"--html={html_report_path}",
        "--self-contained-html",
        f"--alluredir={allure_results_path}"
    ]

    print(f"\n正在执行命令: {' '.join(cmd)}")
    print("=" * 50)

    # 执行命令
    process = subprocess.run(cmd, shell=False, text=True)
    exit_code = process.returncode

    print("=" * 50)
    print(f"Pytest 执行完毕，退出码: {exit_code}")

    # 不要用 shutil.which，直接用绝对路径
    ALLURE_BIN = "/opt/allure-2.36.0/bin/allure"

    # 检查文件是否存在且可执行
    if os.path.exists(ALLURE_BIN) and os.access(ALLURE_BIN, os.X_OK):
        print("\n正在生成 Allure 报告...")

        allure_cmd = [ALLURE_BIN, "generate", allure_results_path, "-o", allure_report_path, "--clean"]

        try:
            # 使用 shell=True 有时能解决 PATH 问题，但这里直接调用更安全
            result = subprocess.run(allure_cmd, check=False, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Allure 报告已生成: {allure_report_path}")
            else:
                print(f"Allure 生成失败 (退出码 {result.returncode}):")
                print(result.stdout)
                print(result.stderr)
        except Exception as e:
            print(f"Allure 命令执行异常: {e}")
    else:
        print(f"\n未找到 Allure 命令或无执行权限: {ALLURE_BIN}")
        print("跳过容器内报告生成，请在宿主机手动生成。")


if __name__ == "__main__":
    main()