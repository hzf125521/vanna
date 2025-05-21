# -*- coding: utf-8 -*-
"""
Project:   vanna
File       vanna.py
Time:      2025/3/25 23:58
Author:    MS28175 Zhifu huang
Email:     hzf125521@163.com
"""

from custom_chat_deepseek import CustomDeepSeekChat
from vanna.chromadb import ChromaDB_VectorStore
from vanna.flask import VannaFlaskApp
from sample_auth import SimplePassword
# import os
# import secrets

api_key = 'sk-af1c6606c7a64cf7b71d20d402eb7355'
model_name = 'deepseek-chat'
language = 'Chinese'


class DeepSeekVanna(ChromaDB_VectorStore, CustomDeepSeekChat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        CustomDeepSeekChat.__init__(self, config=config)


vn = DeepSeekVanna(config={"api_key": api_key, "model": model_name, "language": language})

vn.connect_to_mssql(
    odbc_conn_str='DRIVER={ODBC Driver 17 for SQL Server};SERVER=10.97.14.25,1433;DATABASE=xsteamyj1218;UID=xstadmin;PWD=moonsdb5865')

# vn.connect_to_mssql(
#     odbc_conn_str='DRIVER={ODBC Driver 17 for SQL Server};SERVER=10.97.21.90,1433;DATABASE=xstsql;UID=xstadmin;PWD=moonsdb5865')


import os
# 设置静态文件路径
static_folder = os.path.join(os.path.dirname(__file__), "static")
index_html = os.path.join(static_folder, "index.html")

app = VannaFlaskApp(
    # index_html_path=index_html,
    # assets_folder=os.path.join(static_folder, "assets"),
    vn=vn,
    # auth=SimplePassword(users=[{"email": "admin@example.com", "password": "password"}]),
    allow_llm_to_see_data=True,
    # assets_folder="static",
    logo="./static/my_logo.svg",
    title="智能点检分析助手",
    subtitle=""
)

# # 设置Flask应用的密钥
# app.flask_app.secret_key = secrets.token_hex(16)

app.run()
