import sys
import asyncio

# 【关键】立即设置事件循环策略
print("1. 准备设置事件循环策略...")
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print("2. ✅ 已设置 WindowsSelectorEventLoopPolicy")

# 【关键】在设置之后，再导入 psycopg 相关库！
print("3. 准备导入 psycopg_pool...")
from psycopg_pool import AsyncConnectionPool

# 测试连接（用你的 DB_URI）
DB_URI = "postgresql://kevin:123456@localhost:5432/postgres?sslmode=disable"

async def test():
    print("4. 准备创建连接池...")
    async with AsyncConnectionPool(
        conninfo=DB_URI,
        min_size=1,
        max_size=2,
        kwargs={"autocommit": True, "prepare_threshold": 0}
    ) as pool:
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1;")
                result = await cur.fetchone()
                print(f"5. ✅ 数据库查询成功：{result}")

if __name__ == "__main__":
    asyncio.run(test())