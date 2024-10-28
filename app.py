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
        "01-ai/Yi-1.5-6B-Chat",
        "meta-llama/Meta-Llama-3-70B-Instruct",             
    ]
)


# # 设置环境变量
# if OPENAI_API_KEY:
#     os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# if OPENAI_BASE_URL:
#     os.environ['OPENAI_BASE_URL'] = OPENAI_BASE_URL


# 初始化ell客户端
# ell.init(store='./logdir', autocommit=True, verbose=False)


@st.cache_data
def load_csv(file):
    return pd.read_csv(file)


page = st.sidebar.selectbox("功能", ["速读文献摘要", "检索式"])

if page == "速读文献摘要":
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
                    
                    st.markdown("### 生成总结")
                    for index, row in df.iterrows():
                        title = row['文献标题']
                        abstract = row['摘要']
                        summary = summary_article_by_abstract(title, abstract)
                        
                        # 创建一个可选择的block
                        with st.expander(f"{title}", expanded=True):
                            st.markdown(f"[文章链接]({row['链接']})")
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
                
                    st.markdown("### JSON 格式的总结内容")
                    st.json(summaries)
                    st.markdown("### DataFrame 格式的总结内容")
                    st.dataframe(pd.DataFrame(summaries))
                
                else:
                    st.error("CSV 文件应包含 '文献标题' 和 '摘要' 两列。")
elif page == "检索式":
    st.title("检索式")

    content = {
        "utd": {
            "wos": """SO=("The Accounting Review" OR "Journal of Accounting and Economics" OR "Journal of Accounting Research" OR "Journal of Finance" OR "Journal of Financial Economics" OR "The Review of Financial Studies" OR "Information Systems Research" OR "Journal on Computing" OR "MIS Quarterly" OR "Journal of Consumer Research" OR "Journal of Marketing" OR "Journal of Marketing Research" OR "Marketing Science" OR "Management Science" OR "Operations Research" OR "Journal of Operations Management" OR "Manufacturing and Service Operations Management" OR "Production and Operations Management" OR "Academy of Management Journal" OR "Academy of Management Review" OR "Administrative Science Quarterly" OR "Organization Science" OR "Journal of International Business Studies" OR "Strategic Management Journal")""",
            "scopus": """SRCTITLE ("The Accounting Review" OR "Journal of Accounting and Economics" OR "Journal of Accounting Research" OR "Journal of Finance" OR "Journal of Financial Economics" OR "The Review of Financial Studies" OR "Information Systems Research" OR "Journal on Computing" OR "MIS Quarterly" OR "Journal of Consumer Research" OR "Journal of Marketing" OR "Journal of Marketing Research" OR "Marketing Science" OR "Management Science" OR "Operations Research" OR "Journal of Operations Management" OR "Manufacturing and Service Operations Management" OR "Production and Operations Management" OR "Academy of Management Journal" OR "Academy of Management Review" OR "Administrative Science Quarterly" OR "Organization Science" OR "Journal of International Business Studies" OR "Strategic Management Journal")""",
        
        },
        "ft": {
            "wos": """SO=("Academy of Management Journal" OR "Academy of Management Review" OR "Accounting, Organizations and Society" OR "Administrative Science Quarterly" OR "American Economic Review" OR "Contemporary Accounting Research" OR "Econometrica" OR "Entrepreneurship Theory and Practice" OR "Harvard Business Review" OR "Human Relations" OR "Human Resource Management" OR "Information Systems Research" OR "Journal of Accounting and Economics" OR "Journal of Accounting Research" OR "Journal of Applied Psychology" OR "Journal of Business Ethics" OR "Journal of Business Venturing" OR "Journal of Consumer Psychology" OR "Journal of Consumer Research" OR "Journal of Finance" OR "Journal of Financial and Quantitative Analysis" OR "Journal of Financial Economics" OR "Journal of International Business Studies" OR "Journal of Management" OR "Journal of Management Information Systems" OR "Journal of Management Studies" OR "Journal of Marketing" OR "Journal of Marketing Research" OR "Journal of Operations Management" OR "Journal of Political Economy" OR "Journal of the Academy of Marketing Science" OR "Management Science" OR "Manufacturing and Service Operations Management" OR "Marketing Science" OR "MIS Quarterly" OR "Operations Research" OR "Organization Science" OR "Organization Studies" OR "Organizational Behavior and Human Decision Processes" OR "Production and Operations Management" OR "Quarterly Journal of Economics" OR "Research Policy" OR "Review of Accounting Studies" OR "Review of Economic Studies" OR "Review of Finance" OR "Review of Financial Studies" OR "Sloan Management Review" OR "Strategic Entrepreneurship Journal" OR "Strategic Management Journal" OR "The Accounting Review" OR "Journal of Computing")""",
            "scopus": """SRCTITLE SO=("Academy of Management Journal" OR "Academy of Management Review" OR "Accounting, Organizations and Society" OR "Administrative Science Quarterly" OR "American Economic Review" OR "Contemporary Accounting Research" OR "Econometrica" OR "Entrepreneurship Theory and Practice" OR "Harvard Business Review" OR "Human Relations" OR "Human Resource Management" OR "Information Systems Research" OR "Journal of Accounting and Economics" OR "Journal of Accounting Research" OR "Journal of Applied Psychology" OR "Journal of Business Ethics" OR "Journal of Business Venturing" OR "Journal of Consumer Psychology" OR "Journal of Consumer Research" OR "Journal of Finance" OR "Journal of Financial and Quantitative Analysis" OR "Journal of Financial Economics" OR "Journal of International Business Studies" OR "Journal of Management" OR "Journal of Management Information Systems" OR "Journal of Management Studies" OR "Journal of Marketing" OR "Journal of Marketing Research" OR "Journal of Operations Management" OR "Journal of Political Economy" OR "Journal of the Academy of Marketing Science" OR "Management Science" OR "Manufacturing and Service Operations Management" OR "Marketing Science" OR "MIS Quarterly" OR "Operations Research" OR "Organization Science" OR "Organization Studies" OR "Organizational Behavior and Human Decision Processes" OR "Production and Operations Management" OR "Quarterly Journal of Economics" OR "Research Policy" OR "Review of Accounting Studies" OR "Review of Economic Studies" OR "Review of Finance" OR "Review of Financial Studies" OR "Sloan Management Review" OR "Strategic Entrepreneurship Journal" OR "Strategic Management Journal" OR "The Accounting Review" OR "Journal of Computing")""",
        },
        "tjsem": {
            "wos": """SO=("Academy of Management Journal" OR "Academy of Management Review" OR "Administrative Science Quarterly" OR "American Economic Review" OR "Econometrica" OR "Information Systems Research" OR "Journal of Accounting and Economics" OR "Journal of Accounting Research" OR "Journal of Consumer Research" OR "Journal of Finance" OR "Journal of Financial Economics" OR "Journal of International Business Studies" OR "Journal of Marketing" OR "Journal of Marketing Research" OR "Journal of Operations Management" OR "Journal of Political Economy" OR "Management Information Systems Quarterly" OR "Management Science" OR "Manufacturing & Service Operations Management" OR "Marketing Science" OR "Operations Research" OR "Organization Science" OR "Production and Operations Management" OR "Quarterly Journal of Economics" OR "Review of Economic Studies" OR "Review of Financial Studies" OR "Strategic Management Journal" OR "The Accounting Review" OR "Accounting, Organizations and Society" OR "American Economic Journal: Applied Economics" OR "American Economic Journal: Macroeconomics" OR "American Economic Journal: Microeconomics" OR "American Journal of Agricultural Economics" OR "Contemporary Accounting Research" OR "Entrepreneurship Theory and Practice" OR "Global Environmental Change-Human and Policy Dimensions" OR "Human Resource Management" OR "IEEE Transactions on Automatic Control" OR "International Economic Review" OR "Journal of Applied Psychology" OR "Journal of Business Venturing" OR "Journal of Consumer Psychology" OR "Journal of Development Economics" OR "Journal of Economic Literature" OR "Journal of Economic Theory" OR "Journal of Financial and Quantitative Analysis" OR "Journal of International Economics" OR "Journal of Labor Economics" OR "Journal of Management" OR "Journal of Management Information Systems" OR "Journal of Management Studies" OR "Journal of Monetary Economics" OR "Journal of Public Administration: Research and Theory" OR "Journal of Public Economics" OR "Journal of the Academy of Marketing Science" OR "Journal of Urban Economics" OR "Journal on Computing" OR "Mathematical Programming" OR "Organization Studies" OR "Organizational Behaviour and Human Decision Processes" OR "Personnel Psychology" OR "Policy Studies Journal" OR "Public Administration Review" OR "Public Administration: An International Quarterly" OR "Rand Journal of Economics" OR "Regional Studies" OR "Research Policy" OR "Review of Accounting Studies" OR "Review of Finance" OR "Strategic Entrepreneurship Journal" OR "The Journal of Law and Economics" OR "The Review of Economics and Statistics" OR "Transportation Research Part B: Methodological" OR "Transportation Science" OR "World Development" OR "Abacus-A Journal of Accounting Finance and Business Studies" OR "Academy of Management Perspectives" OR "Accounting and Business Research" OR "Accounting Horizons" OR "American Economic Journal: Economic Policy" OR "American Journal of Sociology" OR "American Review of Public Administration" OR "Annals of Statistics" OR "Asia Pacific Journal of Management" OR "Auditing: A Journal of Practice & Theory" OR "Automation in Construction" OR "British Journal of Management" OR "Business Ethics Quarterly" OR "California Management Review" OR "Canadian Journal of Economics" OR "Computers & Operations Research" OR "Decision Sciences" OR "Decision Support Systems" OR "Ecological Economics" OR "Econometric Theory" OR "Economic Development and Cultural Change" OR "Economic Inquiry" OR "Economic Journal" OR "Economica" OR "Economics Letters" OR "Energy Economics" OR "Energy Journal" OR "Environmental & Resource Economics" OR "European Economic Review" OR "European Journal of Information Systems" OR "European Journal of Operational Research" OR "Experimental Economics" OR "Financial Management" OR "Food Policy" OR "Games and Economic Behavior" OR "Governance–An International Journal of Policy Administration and Institutions" OR "Harvard Business Review" OR "Health Services Research" OR "Human Relations" OR "IEEE Transactions on Engineering Management" OR "IISE Transactions" OR "Industrial Marketing Management" OR "Industrial Relations" OR "Information and Management" OR "International Journal of Human Resource Management" OR "International Journal of Production Economics" OR "International Journal of Project Management" OR "International Journal of Research in Marketing" OR "International Small Business Journal" OR "Journal of Accounting and Public Policy" OR "Journal of Accounting, Auditing and Finance" OR "Journal of Advertising" OR "Journal of Banking & Finance" OR "Journal of Business & Economic Statistics" OR "Journal of Business Ethics" OR "Journal of Business Finance & Accounting" OR "Journal of Comparative Economics" OR "Journal of Construction Engineering and Management" OR "Journal of Corporate Finance" OR "Journal of Econometrics" OR "Journal of Economic Behavior & Organization" OR "Journal of Economic Dynamics & Control" OR "Journal of Economic Geography" OR "Journal of Economic Growth" OR "Journal of Economic Perspectives" OR "Journal of Empirical Finance" OR "Journal of Environmental Economics and Management" OR "Journal of European Public Policy" OR "Journal of Financial Intermediation" OR "Journal of Financial Markets" OR "Journal of Futures Markets" OR "Journal of Health Economics" OR "Journal of Industrial Economics" OR "Journal of Interactive Marketing" OR "Journal of International Money and Finance" OR "Journal of Money, Credit and Banking" OR "Journal of Occupational and Organizational Psychology" OR "Journal of Organizational Behavior" OR "Journal of Policy Analysis and Management" OR "Journal of Product Innovation Management" OR "Journal of Real Estate Finance and Economics" OR "Journal of Regional Science" OR "Journal of Retailing" OR "Journal of Risk and Uncertainty" OR "Journal of Scheduling" OR "Journal of Service Research" OR "Journal of Social Policy" OR "Journal of the American Statistical Association" OR "Journal of the Association for Information Systems" OR "Journal of the European Economic Association" OR "Journal of Transportation Engineering, Part A: Systems" OR "Journal of Vocational Behavior" OR "Journal of World Business" OR "Labour Economics" OR "Land Economics" OR "Leadership Quarterly" OR "Management Accounting Research" OR "Management and Organization Review" OR "Marketing Letters" OR "Mathematical Finance" OR "Mathematics of Operations Research" OR "MIT Sloan Management Review" OR "Naval Research Logistics" OR "Omega-International Journal of Management Science" OR "Organizational Research Methods" OR "Policy and Politics" OR "Psychology & Marketing" OR "Public Management Review" OR "R & D Management" OR "Real Estate Economics" OR "Regional Science & Urban Economics" OR "Regulation and Governance" OR "Review of Economic Dynamics" OR "Risk Analysis" OR "Scandinavian Journal of Economics" OR "Technological Forecasting and Social Change" OR "Technovation" OR "Transportation Research Part A: Policy and Practice" OR "Transportation Research Part E: Logistics and Transportation Review" OR "Accounting and Finance" OR "ACM Transactions on Information Systems" OR "Agricultural Economics" OR "Annals of Operations Research" OR "Applied Economics" OR "Asia Pacific Journal of Human Resources" OR "B E Journal of Macroeconomics" OR "British Journal of Industrial Relations" OR "Business & Society" OR "China Economic Review" OR "Econometric Reviews" OR "Economic Modelling" OR "Economics of Education Review" OR "Entrepreneurship & Regional Development" OR "European Accounting Review" OR "European Journal of Work and Organizational Psychology" OR "Family Business Review" OR "Financial Analysts Journal" OR "Health Economics" OR "Human Resource Management Journal" OR "ILR Review" OR "Information Systems Journal" OR "Insurance: Mathematics and Economics" OR "International Business Review" OR "International Journal of Advertising" OR "International Journal of Electronic Commerce" OR "International Journal of Forecasting" OR "International Journal of Market Research" OR "International Journal of Production Research" OR "Journal of Agricultural Economics" OR "Journal of Business Research" OR "Journal of Derivatives" OR "Journal of Economic Psychology" OR "Journal of Economics & Management Strategy" OR "Journal of Financial Research" OR "Journal of Management Accounting Research" OR "Journal of Management in Engineering" OR "Journal of Managerial Psychology" OR "Journal of Optimization Theory and Applications" OR "Journal of Regulatory Economics" OR "Journal of Risk and Insurance" OR "Journal of Small Business Management" OR "Journal of Strategic Information Systems" OR "Journal of Supply Chain Management" OR "Journal of the American Taxation Association" OR "Journal of the Operational Research Society" OR "Oxford Economic Papers" OR "Oxford Review of Economic Policy" OR "Public Choice" OR "Quantitative Economics" OR "Quantitative Finance" OR "Resource and Energy Economics" OR "Review of Environmental Economics and Policy" OR "Review of Quantitative Finance and Accounting" OR "Service Industries Journal" OR "Supply Chain Management - An International Journal" OR "The International Journal of Accounting")""",
            "scopus": """SRCTITLE ("Academy of Management Journal" OR "Academy of Management Review" OR "Administrative Science Quarterly" OR "American Economic Review" OR "Econometrica" OR "Information Systems Research" OR "Journal of Accounting and Economics" OR "Journal of Accounting Research" OR "Journal of Consumer Research" OR "Journal of Finance" OR "Journal of Financial Economics" OR "Journal of International Business Studies" OR "Journal of Marketing" OR "Journal of Marketing Research" OR "Journal of Operations Management" OR "Journal of Political Economy" OR "Management Information Systems Quarterly" OR "Management Science" OR "Manufacturing & Service Operations Management" OR "Marketing Science" OR "Operations Research" OR "Organization Science" OR "Production and Operations Management" OR "Quarterly Journal of Economics" OR "Review of Economic Studies" OR "Review of Financial Studies" OR "Strategic Management Journal" OR "The Accounting Review" OR "Accounting, Organizations and Society" OR "American Economic Journal: Applied Economics" OR "American Economic Journal: Macroeconomics" OR "American Economic Journal: Microeconomics" OR "American Journal of Agricultural Economics" OR "Contemporary Accounting Research" OR "Entrepreneurship Theory and Practice" OR "Global Environmental Change-Human and Policy Dimensions" OR "Human Resource Management" OR "IEEE Transactions on Automatic Control" OR "International Economic Review" OR "Journal of Applied Psychology" OR "Journal of Business Venturing" OR "Journal of Consumer Psychology" OR "Journal of Development Economics" OR "Journal of Economic Literature" OR "Journal of Economic Theory" OR "Journal of Financial and Quantitative Analysis" OR "Journal of International Economics" OR "Journal of Labor Economics" OR "Journal of Management" OR "Journal of Management Information Systems" OR "Journal of Management Studies" OR "Journal of Monetary Economics" OR "Journal of Public Administration: Research and Theory" OR "Journal of Public Economics" OR "Journal of the Academy of Marketing Science" OR "Journal of Urban Economics" OR "Journal on Computing" OR "Mathematical Programming" OR "Organization Studies" OR "Organizational Behaviour and Human Decision Processes" OR "Personnel Psychology" OR "Policy Studies Journal" OR "Public Administration Review" OR "Public Administration: An International Quarterly" OR "Rand Journal of Economics" OR "Regional Studies" OR "Research Policy" OR "Review of Accounting Studies" OR "Review of Finance" OR "Strategic Entrepreneurship Journal" OR "The Journal of Law and Economics" OR "The Review of Economics and Statistics" OR "Transportation Research Part B: Methodological" OR "Transportation Science" OR "World Development" OR "Abacus-A Journal of Accounting Finance and Business Studies" OR "Academy of Management Perspectives" OR "Accounting and Business Research" OR "Accounting Horizons" OR "American Economic Journal: Economic Policy" OR "American Journal of Sociology" OR "American Review of Public Administration" OR "Annals of Statistics" OR "Asia Pacific Journal of Management" OR "Auditing: A Journal of Practice & Theory" OR "Automation in Construction" OR "British Journal of Management" OR "Business Ethics Quarterly" OR "California Management Review" OR "Canadian Journal of Economics" OR "Computers & Operations Research" OR "Decision Sciences" OR "Decision Support Systems" OR "Ecological Economics" OR "Econometric Theory" OR "Economic Development and Cultural Change" OR "Economic Inquiry" OR "Economic Journal" OR "Economica" OR "Economics Letters" OR "Energy Economics" OR "Energy Journal" OR "Environmental & Resource Economics" OR "European Economic Review" OR "European Journal of Information Systems" OR "European Journal of Operational Research" OR "Experimental Economics" OR "Financial Management" OR "Food Policy" OR "Games and Economic Behavior" OR "Governance–An International Journal of Policy Administration and Institutions" OR "Harvard Business Review" OR "Health Services Research" OR "Human Relations" OR "IEEE Transactions on Engineering Management" OR "IISE Transactions" OR "Industrial Marketing Management" OR "Industrial Relations" OR "Information and Management" OR "International Journal of Human Resource Management" OR "International Journal of Production Economics" OR "International Journal of Project Management" OR "International Journal of Research in Marketing" OR "International Small Business Journal" OR "Journal of Accounting and Public Policy" OR "Journal of Accounting, Auditing and Finance" OR "Journal of Advertising" OR "Journal of Banking & Finance" OR "Journal of Business & Economic Statistics" OR "Journal of Business Ethics" OR "Journal of Business Finance & Accounting" OR "Journal of Comparative Economics" OR "Journal of Construction Engineering and Management" OR "Journal of Corporate Finance" OR "Journal of Econometrics" OR "Journal of Economic Behavior & Organization" OR "Journal of Economic Dynamics & Control" OR "Journal of Economic Geography" OR "Journal of Economic Growth" OR "Journal of Economic Perspectives" OR "Journal of Empirical Finance" OR "Journal of Environmental Economics and Management" OR "Journal of European Public Policy" OR "Journal of Financial Intermediation" OR "Journal of Financial Markets" OR "Journal of Futures Markets" OR "Journal of Health Economics" OR "Journal of Industrial Economics" OR "Journal of Interactive Marketing" OR "Journal of International Money and Finance" OR "Journal of Money, Credit and Banking" OR "Journal of Occupational and Organizational Psychology" OR "Journal of Organizational Behavior" OR "Journal of Policy Analysis and Management" OR "Journal of Product Innovation Management" OR "Journal of Real Estate Finance and Economics" OR "Journal of Regional Science" OR "Journal of Retailing" OR "Journal of Risk and Uncertainty" OR "Journal of Scheduling" OR "Journal of Service Research" OR "Journal of Social Policy" OR "Journal of the American Statistical Association" OR "Journal of the Association for Information Systems" OR "Journal of the European Economic Association" OR "Journal of Transportation Engineering, Part A: Systems" OR "Journal of Vocational Behavior" OR "Journal of World Business" OR "Labour Economics" OR "Land Economics" OR "Leadership Quarterly" OR "Management Accounting Research" OR "Management and Organization Review" OR "Marketing Letters" OR "Mathematical Finance" OR "Mathematics of Operations Research" OR "MIT Sloan Management Review" OR "Naval Research Logistics" OR "Omega-International Journal of Management Science" OR "Organizational Research Methods" OR "Policy and Politics" OR "Psychology & Marketing" OR "Public Management Review" OR "R & D Management" OR "Real Estate Economics" OR "Regional Science & Urban Economics" OR "Regulation and Governance" OR "Review of Economic Dynamics" OR "Risk Analysis" OR "Scandinavian Journal of Economics" OR "Technological Forecasting and Social Change" OR "Technovation" OR "Transportation Research Part A: Policy and Practice" OR "Transportation Research Part E: Logistics and Transportation Review" OR "Accounting and Finance" OR "ACM Transactions on Information Systems" OR "Agricultural Economics" OR "Annals of Operations Research" OR "Applied Economics" OR "Asia Pacific Journal of Human Resources" OR "B E Journal of Macroeconomics" OR "British Journal of Industrial Relations" OR "Business & Society" OR "China Economic Review" OR "Econometric Reviews" OR "Economic Modelling" OR "Economics of Education Review" OR "Entrepreneurship & Regional Development" OR "European Accounting Review" OR "European Journal of Work and Organizational Psychology" OR "Family Business Review" OR "Financial Analysts Journal" OR "Health Economics" OR "Human Resource Management Journal" OR "ILR Review" OR "Information Systems Journal" OR "Insurance: Mathematics and Economics" OR "International Business Review" OR "International Journal of Advertising" OR "International Journal of Electronic Commerce" OR "International Journal of Forecasting" OR "International Journal of Market Research" OR "International Journal of Production Research" OR "Journal of Agricultural Economics" OR "Journal of Business Research" OR "Journal of Derivatives" OR "Journal of Economic Psychology" OR "Journal of Economics & Management Strategy" OR "Journal of Financial Research" OR "Journal of Management Accounting Research" OR "Journal of Management in Engineering" OR "Journal of Managerial Psychology" OR "Journal of Optimization Theory and Applications" OR "Journal of Regulatory Economics" OR "Journal of Risk and Insurance" OR "Journal of Small Business Management" OR "Journal of Strategic Information Systems" OR "Journal of Supply Chain Management" OR "Journal of the American Taxation Association" OR "Journal of the Operational Research Society" OR "Oxford Economic Papers" OR "Oxford Review of Economic Policy" OR "Public Choice" OR "Quantitative Economics" OR "Quantitative Finance" OR "Resource and Energy Economics" OR "Review of Environmental Economics and Policy" OR "Review of Quantitative Finance and Accounting" OR "Service Industries Journal" OR "Supply Chain Management - An International Journal" OR "The International Journal of Accounting")""",
        }
    }

    pattern = {
        "keyword": {
            "wos": """TS=""",
            "scopus": """TITLE-ABS-KEY """
        }
    }

    # 选择器
    selected_category = st.selectbox("类别", ["utd", "ft", "tjsem"])
    selected_source = st.selectbox("数据库", ["wos", "scopus"])

    # 关键词输入框
    keyword = st.text_input("关键词（英文逗号分隔）")
    
    if keyword:
        keywords = keyword.split(",")
        keyword_display = pattern["keyword"][selected_source] + "(" + " OR ".join([f'"{k.strip()}"' for k in keywords]) + ")"
    else:
        keyword_display = ""

    if selected_category and selected_source:
        st.markdown(f"### {selected_category.upper()}")
        content_to_display = content[selected_category][selected_source]
        if keyword_display:
            content_to_display += """ AND """ + keyword_display
        st.code(content_to_display, wrap_lines=True)
