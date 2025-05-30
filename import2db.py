import sqlite3
import pandas as pd

# 创建数据库
conn = sqlite3.connect("northwind.db")
cursor = conn.cursor()

# 导入 SQL 脚本
with open("northwind.sql", "r", encoding="utf-8") as f:
    sql_script = f.read()
cursor.executescript(sql_script)

# 查询示例
df = pd.read_sql("SELECT * FROM Customers LIMIT 5;", conn)
print(df)

conn.close()
