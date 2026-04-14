import mysql.connector
from mysql.connector import pooling
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_POOL_SIZE

# Connection pool for performance
connection_pool = None

def init_db():
    global connection_pool
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name = 'library_pool',
        pool_size = DB_POOL_SIZE,
        host = DB_HOST,
        user = DB_USER,
        password = DB_PASSWORD,
        database = DB_NAME
    )

def get_db():
    """Get the database connection from the pool"""
    return connection_pool.get_connection()

def execute_query(query, params=None, fetch_one=False):
    """Helper function for executing queries"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, params or ())

        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchone() if fetch_one else cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid

        return result
    finally:
        cursor.close()
        conn.close()