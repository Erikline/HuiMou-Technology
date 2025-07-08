import mysql.connector
from mysql.connector import pooling
import logging
from contextlib import contextmanager

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'aidatabase',
    'user': 'root',
    'password': 'xxxxxxx',  # 请修改为实际密码
    'charset': 'utf8mb4',
    'autocommit': True
}

# 创建连接池
connection_pool = pooling.MySQLConnectionPool(
    pool_name="ai_pool",
    pool_size=10,
    pool_reset_session=True,
    **DB_CONFIG
)

@contextmanager
def get_db_connection():
    """获取数据库连接的上下文管理器"""
    connection = None
    try:
        connection = connection_pool.get_connection()
        yield connection
    except mysql.connector.Error as e:
        logging.error(f"Database error: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()

def execute_query(query, params=None, fetch=False):
    """执行SQL查询"""
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            conn.commit()
            return cursor.rowcount
        finally:
            cursor.close()