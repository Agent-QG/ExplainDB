import sqlite3
import os

def convert_sql_to_sqlite(sql_file_path, sqlite_db_path="northwind.db"):
    # 如果数据库文件已存在则先删除（可选）
    if os.path.exists(sqlite_db_path):
        os.remove(sqlite_db_path)

    # 创建新的 SQLite 数据库连接
    conn = sqlite3.connect(sqlite_db_path)
    cursor = conn.cursor()

    # 读取 .sql 文件内容
    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # 执行 SQL 脚本
    try:
        cursor.executescript(sql_script)
        conn.commit()
        print(f"✅ 成功将 {sql_file_path} 导入为 {sqlite_db_path}")
    except Exception as e:
        print("❌ 执行 SQL 脚本出错:", e)
    finally:
        conn.close()

    # 返回 SQLite URL
    return f"sqlite:///{os.path.abspath(sqlite_db_path)}"

# 用法示例
sqlite_url = convert_sql_to_sqlite("northwind.sql")
print("📎 SQLite URL:", sqlite_url)
