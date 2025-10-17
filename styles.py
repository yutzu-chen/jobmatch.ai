import streamlit as st

def apply_global_styles():
    """應用全域 CSS 樣式"""
    st.markdown("""
    <style>
        /* 整體頁面樣式 */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1000px;
        }
        
        /* 主標題 */
        .main-header {
            font-size: 2.5rem;
            font-weight: 300;
            text-align: center;
            color: #1a1a1a;
            margin-bottom: 2rem;
            margin-top: 1rem;
            /* letter-spacing: -0.02em; Safari 兼容性 */
        }
        
        /* 副標題 */
        .subtitle {
            text-align: center;
            color: #666;
            font-size: 1rem;
            margin-bottom: 3rem;
            font-weight: 400;
            line-height: 1.5;
        }
        
        /* 匹配度分數容器 */
        .score-container {
            background: #ffffff;
            border: 1px solid #e1e5e9;
            padding: 2rem;
            border-radius: 8px;
            text-align: center;
            color: #1a1a1a;
            margin: 2rem 0;
            /* box-shadow: 0 1px 3px rgba(0,0,0,0.1); Safari 兼容性 */
        }
        
        .score-number {
            font-size: 3rem;
            font-weight: 200;
            margin: 0;
            color: #1a1a1a;
        }
        
        .score-label {
            font-size: 1rem;
            margin: 0;
            color: #666;
            font-weight: 400;
        }
        
        /* 優先技能標籤 */
        .priority-item {
            background: #f8f9fa;
            color: #495057;
            padding: 0.4rem 0.8rem;
            border-radius: 4px;
            margin: 0.2rem;
            display: inline-block;
            font-weight: 400;
            font-size: 0.9rem;
            border: 1px solid #e9ecef;
        }
        
        /* 符合的經驗項目 */
        .matched-item {
            background: #ffffff;
            border: 1px solid #d4edda;
            padding: 1rem;
            border-radius: 6px;
            margin: 0.5rem 0;
            border-left: 3px solid #28a745;
        }
        
        /* 缺少的經驗項目 */
        .missing-item {
            background: #ffffff;
            border: 1px solid #f8d7da;
            padding: 1rem;
            border-radius: 6px;
            margin: 0.5rem 0;
            border-left: 3px solid #dc3545;
        }
        
        /* AI 建議框 */
        .advice-box {
            background: #ffffff;
            border: 1px solid #e1e5e9;
            color: #1a1a1a;
            padding: 1.5rem;
            border-radius: 6px;
            font-size: 1rem;
            line-height: 1.6;
            margin: 1rem 0;
        }
        
        .advice-box ul {
            padding-left: 1.5rem;
            margin: 0.5rem 0;
        }
        
        .advice-box li {
            margin: 0.5rem 0;
            line-height: 1.6;
        }
        
        .advice-box strong {
            font-weight: 600;
        }
        
        /* 語言選擇器樣式 */
        .stSelectbox > div > div {
            width: 120px !important;
        }
        
        .stSelectbox > div > div > select {
            font-size: 0.9rem !important;
            padding: 0.3rem 0.5rem !important;
            height: 2rem !important;
        }
        
        /* 輸入框樣式 */
        .stTextArea > div > div > textarea {
            border: 1px solid #e1e5e9;
            border-radius: 6px;
            font-size: 0.9rem;
        }
        
        .stTextArea > div > div > textarea:focus {
            border-color: #007bff;
            /* box-shadow: 0 0 0 2px rgba(0,123,255,0.25); Safari 兼容性 */
        }
        
        /* 按鈕樣式 */
        .stButton > button {
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 500;
            transition: background-color 0.2s;
        }
        
        .stButton > button:hover {
            background-color: #0056b3;
        }
        
        /* 側邊欄樣式 */
        .css-1d391kg {
            background-color: #f8f9fa;
        }
        
        /* 標題樣式 */
        h1, h2, h3 {
            color: #1a1a1a;
            font-weight: 500;
        }
        
        /* 移除默認的邊框和陰影 */
        .stApp {
            background-color: #ffffff;
        }
        
        /* 簡化表格樣式 */
        .stDataFrame {
            border: none;
        }
    </style>
    """, unsafe_allow_html=True)