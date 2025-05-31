from sqlalchemy import create_engine, inspect
import core
""""""
# 替换成你的 SQLite 数据库 URL
db_url = "postgresql+psycopg2://postgres:226850@localhost:5433/northwind"

# 创建 SQLAlchemy 引擎
engine = create_engine(db_url)

# 创建数据库检查器
inspector = inspect(engine)

# 获取所有表名
tables = inspector.get_table_names()

# 遍历每个表并输出字段结构
for table in tables:
    print(f"📋 Table: {table}")
    columns = inspector.get_columns(table)
    for col in columns:
        name = col['name']
        dtype = col['type']
        nullable = col['nullable']
        default = col.get('default', None)
        print(f"  - {name} ({dtype}) | Nullable: {nullable} | Default: {default}")
    print("-" * 40)

print("DB tables done!!!!!!!")
question = "What is the average value of an order for each customer segment over the past year 1997?"
result = core.process_query(db_uri="postgresql+psycopg2://postgres:226850@localhost:5433/northwind",question=question)
chart_base64_list = result["chart_base64_list"]
print(chart_base64_list[2])