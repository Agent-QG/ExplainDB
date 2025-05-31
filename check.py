import sqlite3

# 连接数据库
conn = sqlite3.connect("Chinook.db")
cursor = conn.cursor()

# 查询 2009 年有交易记录的国家
query = """
SELECT COUNT(*) 
FROM (
    SELECT c.CustomerId
    FROM Customer c
    JOIN Invoice i ON c.CustomerId = i.CustomerId
    GROUP BY c.CustomerId
    HAVING  
        SUM(CASE WHEN strftime('%Y', i.InvoiceDate) = '2010' THEN i.Total ELSE 0 END) > 0
        AND
        SUM(CASE WHEN strftime('%Y', i.InvoiceDate) = '2011' THEN i.Total ELSE 0 END) >= 
            1.5 * SUM(CASE WHEN strftime('%Y', i.InvoiceDate) = '2010' THEN i.Total ELSE 0 END)
);


"""

cursor.execute(query)
results = cursor.fetchall()

# 输出结果
print(results)

# 关闭连接
cursor.close()
conn.close()
