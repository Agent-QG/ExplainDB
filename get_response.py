import openai
import os
os.environ["OPENAI_API_KEY"] = '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'
from openai import OpenAI

# 初始化 OpenAI 客户端（推荐使用环境变量存储 key）
client = OpenAI(api_key='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')  # 或省略该行，使用默认方式加载密钥
with open("db.txt", "r", encoding="utf-8") as f:
    db_structure = f.read()
# 调用 Chat Completion 接口
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "你是一个精通 SQL 的助手，下面是数据库结构：\n" + db_structure},
        {"role": "user", "content": "哪10位演员（不论男女）演了最多部评分大于等于5.0的电影？请给出 SQL 语句"}
    ],
    temperature=1.0,
    top_p=1.0,
    max_tokens=2048
)

# 输出返回内容
print(response.choices[0].message.content)
