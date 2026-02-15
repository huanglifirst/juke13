# test_postgres_conn.py
import asyncio
import sys
from psycopg_pool import AsyncConnectionPool

# 先设置Windows兼容的事件循环（和你的项目一致）
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 你的DB_URI
DB_URI = "postgresql://kevin:123456@localhost:5432/postgres?sslmode=disable"

async def test_postgres_connection():
    """测试PostgreSQL异步连接"""
    try:
        # 创建连接池（和项目中一致的配置）
        async with AsyncConnectionPool(
            conninfo=DB_URI,
            min_size=5,
            max_size=10,
            kwargs={"autocommit": True, "prepare_threshold": 0}
        ) as pool:
            # 执行简单查询验证连接
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT version();")
                    version = await cur.fetchone()
                    print(f"✅ 连接成功！PostgreSQL版本：{version[0]}")
                    
                    # 验证用户权限（查询当前用户）
                    await cur.execute("SELECT current_user;")
                    user = await cur.fetchone()
                    print(f"✅ 当前登录用户：{user[0]}")
                    
                    # 验证数据库名
                    await cur.execute("SELECT current_database();")
                    db = await cur.fetchone()
                    print(f"✅ 当前数据库：{db[0]}")
    except Exception as e:
        print(f"❌ 连接失败：{str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_postgres_connection())