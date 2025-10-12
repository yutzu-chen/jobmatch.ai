import streamlit as st
import json
from groq import Groq
import os
from dotenv import load_dotenv
import time

# 載入環境變數
load_dotenv()

# 頁面配置
st.set_page_config(
    page_title="MatchMe.AI - AI 履歷職缺匹配分析工具",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義 CSS 樣式 - 簡約風格
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
        letter-spacing: -0.02em;
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
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
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
    
    /* 輸入框樣式 */
    .stTextArea > div > div > textarea {
        border: 1px solid #e1e5e9;
        border-radius: 6px;
        font-size: 0.9rem;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #007bff;
        box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
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

def get_ui_texts(language):
    """根據語言返回界面文字"""
    texts = {
        "中文": {
            "app_title": "JobMatch.AI",
            "app_subtitle": "看見你的強項，精準補齊差距：30 秒搞懂這份職缺適不適合你",
            "settings_title": "設置",
            "language_label": "分析語言",
            "instructions_title": "使用說明",
            "instructions": [
                "在左側貼上你的履歷內容",
                "在右側貼上職缺描述",
                "點擊「開始分析」",
                "查看匹配度結果和建議"
            ],
            "privacy_title": "隱私保護",
            "privacy": [
                "不保存任何履歷內容",
                "分析完成後自動清除",
                "完全免費使用"
            ],
            "resume_title": "履歷內容",
            "resume_placeholder": "請貼上你的履歷內容（支援中英文）",
            "resume_example": "例如：\n姓名：張小明\n學歷：台灣大學資訊工程系\n工作經驗：\n- 2020-2022 軟體工程師，負責前端開發\n- 具備 React, JavaScript, Python 經驗\n...",
            "job_title": "職缺描述",
            "job_placeholder": "請貼上職缺描述（Job Description）",
            "job_example": "例如：\n職位：前端工程師\n要求：\n- 3年以上 React 開發經驗\n- 熟悉 JavaScript, TypeScript\n- 具備團隊協作能力\n- 有產品思維\n...",
            "analyze_button": "開始分析",
            "analyze_another": "分析另一份職缺",
            "match_score_label": "總體匹配度",
            "priorities_title": "職缺關鍵技能",
            "matched_title": "我符合的經驗",
            "missing_title": "我缺少的經驗",
            "advice_title": "AI 建議",
            "no_matched": "暫無符合的經驗",
            "all_skills_met": "所有關鍵技能都已具備！",
            "copy_advice": "複製建議文字",
            "analyzing": "AI 正在分析中，請稍候...",
            "analysis_complete": "分析完成！",
            "analysis_failed": "分析失敗，請檢查 API 設置或稍後再試",
            "fill_required": "請填寫履歷內容和職缺描述"
        },
        "English": {
            "app_title": "JobMatch.AI",
            "app_subtitle": "See your strengths, bridge the gaps: 30 seconds to know if this job fits you",
            "settings_title": "Settings",
            "language_label": "Analysis Language",
            "instructions_title": "Instructions",
            "instructions": [
                "Paste your resume content on the left",
                "Paste job description on the right",
                "Click 'Start Analysis'",
                "View matching results and recommendations"
            ],
            "privacy_title": "Privacy Protection",
            "privacy": [
                "No resume content is saved",
                "Automatically cleared after analysis",
                "Completely free to use"
            ],
            "resume_title": "Resume Content",
            "resume_placeholder": "Please paste your resume content (supports multiple languages)",
            "resume_example": "Example:\nName: John Smith\nEducation: Computer Science, MIT\nExperience:\n- 2020-2022 Software Engineer, Frontend Development\n- Proficient in React, JavaScript, Python\n...",
            "job_title": "Job Description",
            "job_placeholder": "Please paste job description",
            "job_example": "Example:\nPosition: Frontend Engineer\nRequirements:\n- 3+ years React development experience\n- Familiar with JavaScript, TypeScript\n- Team collaboration skills\n- Product mindset\n...",
            "analyze_button": "Start Analysis",
            "analyze_another": "Analyze Another Job",
            "match_score_label": "Overall Match Score",
            "priorities_title": "Job Key Skills",
            "matched_title": "My Matching Experience",
            "missing_title": "Missing Experience",
            "advice_title": "AI Recommendations",
            "no_matched": "No matching experience found",
            "all_skills_met": "All key skills are met!",
            "copy_advice": "Copy Recommendations",
            "analyzing": "AI is analyzing, please wait...",
            "analysis_complete": "Analysis complete!",
            "analysis_failed": "Analysis failed, please check API settings or try again later",
            "fill_required": "Please fill in resume content and job description"
        },
    }
    return texts.get(language, texts["中文"])

def initialize_groq_client():
    """初始化 Groq 客戶端"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("⚠️ 請設置 GROQ_API_KEY 環境變數")
        st.info("請到 https://console.groq.com/ 申請免費 API key，然後在 .env 文件中設置")
        return None
    
    try:
        client = Groq(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"❌ Groq 客戶端初始化失敗: {str(e)}")
        return None

def analyze_resume_job_match(resume_text, job_description, language="中文"):
    """使用 Groq API 分析履歷與職缺匹配度"""
    
    client = initialize_groq_client()
    if not client:
        return None
    
    # 系統提示詞
    system_prompt = f"""你是專業職涯顧問。請閱讀【履歷】與【職缺】，並 ONLY 以 JSON 回覆，符合下列 schema：

{{
  "match_score": 整數0-100,
  "confidence": 浮點0-1,
  "priorities": [{{"name":字串,"weight":0-1}}],
  "matched": [{{"item":字串,"evidence":[字串...]}}],
  "missing": [{{"item":字串,"action":字串}}],
  "advice": 字串(3-5句)
}}

規則：
- 所有回應文字必須使用{language}
- priorities 依 JD 語義排序（設計系統、Web框架、AI in UI、跨平台協作、溝通/對齊...）
- matched/missing 需以履歷/職缺原文為佐證（給 evidence）
- advice 語氣自然，給可落地的一週行動
- 僅回 JSON，不要其他文字"""

    user_prompt = f"""
履歷內容：
{resume_text}

職缺描述：
{job_description}

請分析匹配度並提供建議。
"""

    try:
        # 創建聊天完成
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=1000
        )
        
        response_text = chat_completion.choices[0].message.content
        
        # 嘗試解析 JSON
        try:
            # 清理回應文本，提取 JSON 部分
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                json_text = response_text
            
            result = json.loads(json_text)
            return result
            
        except json.JSONDecodeError as e:
            st.error(f"❌ JSON 解析失敗: {str(e)}")
            st.text("原始回應:")
            st.text(response_text)
            return None
            
    except Exception as e:
        st.error(f"❌ API 調用失敗: {str(e)}")
        return None

def display_results(result, language="中文"):
    """顯示分析結果"""
    if not result:
        return
    
    # 根據語言設置文字
    texts = get_ui_texts(language)
    
    # 匹配度分數
    match_score = result.get('match_score', 0)
    confidence = result.get('confidence', 0)
    
    # 計算信心指標
    confidence_text = ""
    if confidence >= 0.8:
        confidence_text = "高信心度"
        confidence_color = "#28a745"
    elif confidence >= 0.6:
        confidence_text = "中等信心度"
        confidence_color = "#ffc107"
    else:
        confidence_text = "低信心度"
        confidence_color = "#dc3545"
    
    st.markdown(f"""
    <div class="score-container">
        <h1 class="score-number">{match_score}%</h1>
        <p class="score-label">{texts['match_score_label']}</p>
        <p style="font-size: 0.9rem; margin-top: 0.5rem; color: {confidence_color}; font-weight: 500;">{confidence_text}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 職缺關鍵技能
    if 'priorities' in result and result['priorities']:
        st.markdown(f"### {texts['priorities_title']}")
        
        # 顯示技能分數解釋
        if 'score_explanation' in result and result['score_explanation']:
            st.markdown(f"<p style='font-size: 0.9rem; color: #666; margin-bottom: 1rem;'>{result['score_explanation']}</p>", unsafe_allow_html=True)
        
        # 顯示技能和權重
        for i, priority in enumerate(result['priorities'], 1):
            if isinstance(priority, dict):
                name = priority.get('name', '')
                weight = priority.get('weight', 0)
                weight_percent = int(weight * 100)
                color = "#28a745" if weight >= 0.7 else "#ffc107" if weight >= 0.5 else "#dc3545"
                
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; 
                           background: #f8f9fa; padding: 0.8rem; margin: 0.3rem 0; border-radius: 6px; 
                           border-left: 3px solid {color};">
                    <span style="font-weight: 500;">{i}. {name}</span>
                    <span style="font-weight: bold; color: {color};">{weight_percent}%</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                # 兼容舊格式
                st.markdown(f"<div class='priority-item'>{i}. {priority}</div>", unsafe_allow_html=True)
    
    # 雙欄結果
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {texts['matched_title']}")
        if 'matched' in result and result['matched']:
            for item in result['matched']:
                # 處理新格式（有item和evidence）或舊格式
                if isinstance(item, dict) and 'item' in item and 'evidence' in item:
                    evidence_text = "、".join(item['evidence'][:2])  # 只顯示前2個證據
                    st.markdown(f'''
                    <div class="matched-item">
                        <strong>{item["item"]}</strong><br>
                        <small style="color: #666; font-style: italic;">來自履歷：{evidence_text}</small>
                    </div>
                    ''', unsafe_allow_html=True)
                elif isinstance(item, dict) and 'title' in item and 'description' in item:
                    st.markdown(f'<div class="matched-item"><strong>{item["title"]}</strong><br>{item["description"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="matched-item">{item}</div>', unsafe_allow_html=True)
        else:
            st.info(texts['no_matched'])
    
    with col2:
        st.markdown(f"### {texts['missing_title']}")
        if 'missing' in result and result['missing']:
            for item in result['missing']:
                # 處理新格式（有item和action）或舊格式
                if isinstance(item, dict) and 'item' in item and 'action' in item:
                    st.markdown(f'''
                    <div class="missing-item">
                        <strong>{item["item"]}</strong><br>
                        <small style="color: #666; font-style: italic;">建議行動：{item["action"]}</small>
                    </div>
                    ''', unsafe_allow_html=True)
                elif isinstance(item, dict) and 'title' in item and 'description' in item:
                    st.markdown(f'<div class="missing-item"><strong>{item["title"]}</strong><br>{item["description"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="missing-item">{item}</div>', unsafe_allow_html=True)
        else:
            st.success(texts['all_skills_met'])
    
    # AI 建議
    if 'advice' in result and result['advice']:
        st.markdown(f"### {texts['advice_title']}")
        
        advice_content = result['advice']
        
        # 處理新格式（字符串）或舊格式（字典/列表）
        if isinstance(advice_content, str):
            # 新格式：直接顯示字符串建議
            advice_html = advice_content
        elif isinstance(advice_content, dict):
            # 舊格式：處理分類建議
            advice_html = ""
            
            # 立即行動建議
            if 'immediate_actions' in advice_content and advice_content['immediate_actions']:
                advice_html += "<h4 style='color: #dc3545; margin-top: 1rem;'>立即行動</h4><ul>"
                for item in advice_content['immediate_actions']:
                    clean_item = item.replace("立即行動：", "").replace("立即行動:", "").strip()
                    advice_html += f"<li>{clean_item}</li>"
                advice_html += "</ul>"
            
            # 技能發展建議
            if 'skill_development' in advice_content and advice_content['skill_development']:
                advice_html += "<h4 style='color: #007bff; margin-top: 1rem;'>技能發展</h4><ul>"
                for item in advice_content['skill_development']:
                    clean_item = item.replace("技能發展：", "").replace("技能發展:", "").replace("技能提升：", "").replace("技能提升:", "").strip()
                    advice_html += f"<li>{clean_item}</li>"
                advice_html += "</ul>"
            
            # 職涯指導建議
            if 'career_guidance' in advice_content and advice_content['career_guidance']:
                advice_html += "<h4 style='color: #28a745; margin-top: 1rem;'>職涯指導</h4><ul>"
                for item in advice_content['career_guidance']:
                    clean_item = item.replace("職涯指導：", "").replace("職涯指導:", "").replace("職涯發展：", "").replace("職涯發展:", "").strip()
                    advice_html += f"<li>{clean_item}</li>"
                advice_html += "</ul>"
        elif isinstance(advice_content, list):
            advice_html = "<ul>"
            for item in advice_content:
                advice_html += f"<li>{item}</li>"
            advice_html += "</ul>"
        else:
            advice_html = str(advice_content)
        
        st.markdown(f'<div class="advice-box">{advice_html}</div>', unsafe_allow_html=True)

def main():
    # 側邊欄設置（先設置語言）
    with st.sidebar:
        language = st.selectbox("語言", ["中文", "English"], index=0)
    
    # 根據選擇的語言獲取文字
    texts = get_ui_texts(language)
    
    # 主標題
    st.markdown(f'<h1 class="main-header">{texts["app_title"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{texts["app_subtitle"]}</p>', unsafe_allow_html=True)
    
    # 側邊欄設置
    with st.sidebar:
        st.markdown(f"### {texts['settings_title']}")
        
        st.markdown(f"### {texts['instructions_title']}")
        for i, instruction in enumerate(texts['instructions'], 1):
            st.markdown(f"{i}. {instruction}")
        
        st.markdown(f"### {texts['privacy_title']}")
        for privacy_item in texts['privacy']:
            st.markdown(f"- {privacy_item}")
    
    # 主要輸入區域
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {texts['resume_title']}")
        resume_text = st.text_area(
            texts['resume_placeholder'],
            height=300,
            placeholder=texts['resume_example']
        )
    
    with col2:
        st.markdown(f"### {texts['job_title']}")
        job_description = st.text_area(
            texts['job_placeholder'],
            height=300,
            placeholder=texts['job_example']
        )
    
    # 分析按鈕
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
    with col_btn2:
        analyze_button = st.button(
            texts['analyze_button'],
            type="primary",
            use_container_width=True
        )
    
    # 執行分析
    if analyze_button:
        if not resume_text.strip() or not job_description.strip():
            st.error(texts['fill_required'])
            return
        
        with st.spinner(texts['analyzing']):
            result = analyze_resume_job_match(resume_text, job_description, language)
        
        if result:
            st.success(texts['analysis_complete'])
            display_results(result, language)
            
            # 重新分析按鈕
            st.markdown("<br>", unsafe_allow_html=True)
            col_new1, col_new2, col_new3 = st.columns([1, 2, 1])
            with col_new2:
                if st.button(texts['analyze_another'], use_container_width=True):
                    st.rerun()
        else:
            st.error(texts['analysis_failed'])

if __name__ == "__main__":
    main()
