import streamlit as st
import json
import google.generativeai as genai
import os
import hashlib
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 頁面配置
st.set_page_config(
    page_title="JobMatch.AI - Test",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 極簡 CSS
st.markdown("""
<style>
    .main .block-container {
        padding: 1rem;
    }
    .test-box {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def get_ui_texts(language):
    """根據語言返回界面文字"""
    texts = {
        "中文": {
            "app_title": "JobMatch.AI",
            "app_subtitle": "測試版本",
            "resume_title": "履歷內容",
            "job_title": "職缺描述",
            "analyze_button": "開始分析",
            "analyzing": "分析中...",
            "analysis_complete": "分析完成！",
            "analysis_failed": "分析失敗，請稍後再試"
        },
        "English": {
            "app_title": "JobMatch.AI",
            "app_subtitle": "Test Version",
            "resume_title": "Resume Content",
            "job_title": "Job Description",
            "analyze_button": "Start Analysis",
            "analyzing": "Analyzing...",
            "analysis_complete": "Analysis Complete!",
            "analysis_failed": "Analysis failed, please try again"
        }
    }
    return texts.get(language, texts["中文"])

def initialize_gemini_client():
    """初始化 Gemini 客戶端"""
    try:
        # 優先使用 Hugging Face 環境變數，然後是本地 .env 文件
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('HF_GOOGLE_API_KEY')
        if not api_key:
            st.error("❌ 請設置 GOOGLE_API_KEY 或 HF_GOOGLE_API_KEY 環境變數")
            return None
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        return model
    except Exception as e:
        st.error(f"❌ Gemini 客戶端初始化失敗: {str(e)}")
        return None

def simple_analysis(resume_text, job_description, language):
    """簡化版分析"""
    model = initialize_gemini_client()
    if not model:
        return None
    
    prompt = f"""請用{language}分析以下履歷和職缺的匹配度，並以 JSON 格式回覆：

履歷：{resume_text[:500]}
職缺：{job_description[:500]}

請回覆：
{{
  "match_score": 75,
  "match_explanation": "簡短說明匹配度",
  "summary": "分析摘要"
}}"""

    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text)
        return result
    except Exception as e:
        st.error(f"分析失敗: {str(e)}")
        return None

def main():
    # 語言選擇
    language = st.selectbox("語言 / Language", ["中文", "English"])
    texts = get_ui_texts(language)
    
    # 標題
    st.markdown(f'<h1 style="text-align: center;">{texts["app_title"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; color: #666;">{texts["app_subtitle"]}</p>', unsafe_allow_html=True)
    
    # 測試訊息
    st.markdown("""
    <div class="test-box">
        <strong>📱 Safari 兼容性測試</strong><br>
        如果你看到這個訊息，表示基本功能正常。
    </div>
    """, unsafe_allow_html=True)
    
    # 輸入區域
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {texts['resume_title']}")
        resume_text = st.text_area("", placeholder="請貼上履歷內容...", height=200)
    
    with col2:
        st.markdown(f"### {texts['job_title']}")
        job_description = st.text_area("", placeholder="請貼上職缺描述...", height=200)
    
    # 分析按鈕
    if st.button(texts['analyze_button'], use_container_width=True):
        if not resume_text or not job_description:
            st.warning("請填寫履歷內容和職缺描述")
            return
        
        with st.spinner(texts['analyzing']):
            result = simple_analysis(resume_text, job_description, language)
        
        if result:
            st.success(texts['analysis_complete'])
            
            # 顯示結果
            st.markdown(f"""
            <div class="test-box">
                <h3>匹配度: {result.get('match_score', 0)}%</h3>
                <p>{result.get('match_explanation', '')}</p>
                <p><strong>摘要:</strong> {result.get('summary', '')}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(texts['analysis_failed'])

if __name__ == "__main__":
    main()
