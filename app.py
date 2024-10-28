import os
from openai import OpenAI

if os.getenv('PRODUCTION'):
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        base_url=os.getenv('OPENAI_BASE_URL')
    )
else:
    from dotenv import find_dotenv, load_dotenv
    load_dotenv(find_dotenv())
    assert load_dotenv(find_dotenv())
    assert os.getenv('OPENAI_API_KEY')
    assert os.getenv('OPENAI_BASE_URL')
    
    client = OpenAI()

import streamlit as st
import pandas as pd
import ell


st.set_page_config(page_title="速读文献摘要", 
                   page_icon="./public/logo.png")


# 设置LLM模型
# st.sidebar.title("LLM 设置")
# OPENAI_API_KEY = st.sidebar.text_input("OPENAI_API_KEY", type="password")
# OPENAI_BASE_URL = st.sidebar.text_input("OPENAI_BASE_URL")
# MODEL_NAME = st.sidebar.text_input("MODEL_NAME")
MODEL_NAME = st.sidebar.selectbox(
    "选择模型", 
    [
        "Qwen/Qwen2-7B-Instruct",
        "THUDM/glm-4-9b-chat",
        "01-ai/Yi-1.5-6B-Chat"                  
    ]
)


# # 设置环境变量
# if OPENAI_API_KEY:
#     os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# if OPENAI_BASE_URL:
#     os.environ['OPENAI_BASE_URL'] = OPENAI_BASE_URL


# 初始化ell客户端
# ell.init(store='./logdir', autocommit=True, verbose=False)


if not MODEL_NAME:
    st.warning("请设置模型")
else:    
    @ell.simple(model=MODEL_NAME, client=client, temperature=0.5)
    def summary_article_by_abstract(title: str, abstract: str):
        """你是一名IS领域的教授。请根据学生发送的文章题目和摘要，帮助总结文章的内容。要求：不要产生幻觉；使用中文；你需要返回字符串格式的总结的内容；"""
        return f"文章名称：{title}；\n文章摘要：{abstract}；"

    # Streamlit 页面布局
    st.title("速读文献摘要")
    st.write("请上传 Scopus 导出的包含文章标题和摘要的 CSV 文件")

    # 初始化 session state
    if 'process_clicked' not in st.session_state:
        st.session_state.process_clicked = False

    # 文件上传
    uploaded_file = st.file_uploader("上传 CSV 文件", type=["csv"])

    @st.cache_data
    def load_csv(file):
        return pd.read_csv(file)

    if uploaded_file is not None:
        # 处理按钮
        if st.button("处理文件"):
            st.session_state.process_clicked = True
        
            # 读取 CSV 文件并缓存
            df = load_csv(uploaded_file)

            # 检查数据框是否包含正确的列
            if '文献标题' in df.columns and '摘要' in df.columns:
                total_rows = len(df)
                progress_bar = st.progress(0)
                progress_text = st.empty()  # 用于显示当前进度
                summaries = []  # 用于存储总结内容
                
                st.write("生成总结")
                for index, row in df.iterrows():
                    title = row['文献标题']
                    abstract = row['摘要']
                    summary = summary_article_by_abstract(title, abstract)
                    
                    # 创建一个可选择的block
                    with st.expander(f"{title}", expanded=True):
                        st.write(f"{summary}")

                    summaries.append(
                        {
                            "title": title,
                            "summary": summary,
                        }
                    )
                    
                    # 更新进度条
                    progress_bar.progress((index + 1) / total_rows)
                    # 更新进度文本
                    progress_text.text(f"处理进度: {index + 1}/{total_rows}")
            
                st.write("Json格式的总结内容")
                st.json(summaries)
                st.write("DataFrame格式的总结内容")
                st.dataframe(pd.DataFrame(summaries))
            
            else:
                st.error("CSV 文件应包含 '文献标题' 和 '摘要' 两列。")