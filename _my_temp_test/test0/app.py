# -*- coding: utf-8 -*-
"""
Project:   vanna
File       vanna.py
Time:      2025/3/25 23:58
Author:    MS28175 Zhifu huang
Email:     hzf125521@163.com
"""

from openai import OpenAI
from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore
from vanna.flask import VannaFlaskApp

api_key = 'sk-af1c6606c7a64cf7b71d20d402eb7355'
my_llm_base_url = 'https://api.deepseek.com/'  # IP和端口号改为你自己的，我这里实际用的我的云服务器的地址
my_llm_name = 'deepseek-chat'

language = 'Chinese'

# 初始化客户端
client = OpenAI(
    api_key=api_key,
    base_url=my_llm_base_url,
    default_headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
)


class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, client=None, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, client=client, config=config)


# 使用自定义的大模型及vanna提供的向量库
vn = MyVanna(client=client, config={"model": my_llm_name, "language": language})

vn.connect_to_mssql(
    odbc_conn_str='DRIVER={ODBC Driver 17 for SQL Server};SERVER=10.97.14.25,1433;DATABASE=xsteamyj1218;UID=xstadmin;PWD=moonsdb5865')

# vn.ask(question="“2#抄浆MCC室”设备最近15天的漏检率变化趋势？", auto_train=False, allow_llm_to_see_data=True)

app = VannaFlaskApp(
    vn,
    allow_llm_to_see_data=True
)
app.run()
