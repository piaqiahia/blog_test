import sys

sys.path.insert(0, 'F:/test_project')

from app import create_app
from flask import current_app

# 创建应用
app = create_app()

# 创建应用上下文
with app.app_context():
    from app.ext import cache

    print("=" * 60)
    print("测试 Flask-Caching 是否使用 Redis")
    print("=" * 60)

    # 检查缓存配置
    print(f"\n1. 缓存配置:")
    print(f"   CACHE_TYPE = {app.config.get('CACHE_TYPE')}")
    print(f"   CACHE_REDIS_URL = {app.config.get('CACHE_REDIS_URL')}")

    # 检查缓存实例的配置
    print(f"\n2. Flask-Caching 实例配置:")
    print(f"   cache.config = {cache.config}")

    # 测试缓存写入
    print(f"\n3. 测试缓存操作:")
    try:
        # 写入缓存
        cache.set('flask_test_key', 'Hello from Flask-Caching!', timeout=60)
        print(f"   ✅ 写入缓存: 'flask_test_key' = 'Hello from Flask-Caching!'")

        # 读取缓存
        value = cache.get('flask_test_key')
        print(f"   ✅ 读取缓存: {value}")

        # 验证值是否正确
        if value == 'Hello from Flask-Caching!':
            print(f"   ✅ 缓存值正确!")
        else:
            print(f"   ❌ 缓存值不正确!")

        # 删除缓存
        cache.delete('flask_test_key')
        print(f"   ✅ 删除缓存")

        # 验证已删除
        value_after_delete = cache.get('flask_test_key')
        if value_after_delete is None:
            print(f"   ✅ 缓存已成功删除")
        else:
            print(f"   ❌ 缓存删除失败")

    except Exception as e:
        print(f"   ❌ 缓存操作失败: {e}")
        import traceback

        traceback.print_exc()

    print("=" * 60)
    print("测试完成!")
    print("=" * 60)