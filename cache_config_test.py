import redis
import os
import sys

# 添加项目路径
sys.path.insert(0, 'F:/test_project')

# 从 Flask app.config 读取配置
from app import create_app

app = create_app()

cache_type = app.config.get('CACHE_TYPE', 'SimpleCache')
redis_url = app.config.get('CACHE_REDIS_URL', 'redis://localhost:6379/0')

print(f"从 Flask app.config 读取的配置:")
print(f"  CACHE_TYPE = {cache_type}")
print(f"  CACHE_REDIS_URL = {redis_url}")

if cache_type == 'RedisCache':
    try:
        # 连接 Redis
        r = redis.from_url(redis_url)

        # 测试连接
        r.ping()
        print("✅ 成功连接到 Redis!")

        # 测试读写
        r.set('test_key', 'Hello Redis!')
        value = r.get('test_key')
        print(f"从 Redis 读取的值: {value.decode('utf-8')}")

    except Exception as e:
        print(f"❌ 连接 Redis 失败: {e}")
else:
    print(f"当前缓存类型: {cache_type}, 未使用 Redis")