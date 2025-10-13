import streamlit as st
import json
import google.generativeai as genai
import os
import hashlib
from dotenv import load_dotenv
import time

# 載入環境變數
load_dotenv()

# 頁面配置
st.set_page_config(
    page_title="JobMatch.AI - AI 履歷職缺匹配分析工具",
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
        font-size: 0.8rem !important;
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
            "priorities_title": "職缺關鍵經驗/技能",
            "matched_title": "我符合的經驗",
            "missing_title": "我缺少的經驗",
            "advice_title": "AI 建議",
            "advice_resume_optimization": "履歷優化",
            "advice_cover_letter": "求職信建議",
            "advice_skill_gap": "技能差距分析",
            "advice_interview": "面試準備建議",
            "advice_portfolio": "作品集建議",
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
            "resume_placeholder": "Please paste your resume content",
            "resume_example": "Example:\nName: John Smith\nEducation: Computer Science, MIT\nExperience:\n- 2020-2022 Software Engineer, Frontend Development\n- Proficient in React, JavaScript, Python\n...",
            "job_title": "Job Description",
            "job_placeholder": "Please paste job description",
            "job_example": "Example:\nPosition: Frontend Engineer\nRequirements:\n- 3+ years React development experience\n- Familiar with JavaScript, TypeScript\n- Team collaboration skills\n- Product mindset\n...",
            "analyze_button": "Start Analysis",
            "analyze_another": "Analyze Another Job",
            "match_score_label": "Overall Match Score",
            "priorities_title": "Job Key Experience/Skills",
            "matched_title": "My Matching Experience",
            "missing_title": "Missing Experience",
            "advice_title": "AI Recommendations",
            "advice_resume_optimization": "Resume Optimization",
            "advice_cover_letter": "Cover Letter Suggestions",
            "advice_skill_gap": "Skill Gap Analysis",
            "advice_interview": "Interview Preparation",
            "advice_portfolio": "Portfolio Suggestions",
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

def initialize_gemini_client():
    """初始化 Google Gemini 客戶端"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("⚠️ 請設置 GOOGLE_API_KEY 環境變數")
        st.info("請到 https://makersuite.google.com/app/apikey 申請免費 API key，然後在 .env 文件中設置")
        return None
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        return model
    except Exception as e:
        st.error(f"❌ Gemini 客戶端初始化失敗: {str(e)}")
        return None

def detect_language(text):
    """檢測文本的主要語言"""
    # 更準確的語言檢測邏輯
    chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
    english_chars = len([c for c in text if c.isalpha() and ord(c) < 128])
    total_chars = chinese_chars + english_chars
    
    if total_chars == 0:
        return "English"  # 預設英文
    
    chinese_ratio = chinese_chars / total_chars
    # 提高閾值，只有當中文字符佔比超過 50% 時才認為是中文
    return "中文" if chinese_ratio > 0.5 else "English"

def analyze_resume_job_match(resume_text, job_description, ui_language="中文"):
    """使用 Google Gemini API 分析履歷與職缺匹配度"""
    
    # 自動檢測履歷和職缺的語言
    resume_lang = detect_language(resume_text)
    job_lang = detect_language(job_description)
    
    # 優先使用履歷語言，如果履歷和職缺語言不同，則使用履歷語言
    detected_language = resume_lang
    
    # 創建輸入的哈希值用於緩存（包含檢測到的語言）
    input_hash = hashlib.md5(f"{resume_text}_{job_description}_{detected_language}".encode()).hexdigest()
    
    # 檢查是否已有緩存結果
    if 'analysis_cache' not in st.session_state:
        st.session_state.analysis_cache = {}
    
    if input_hash in st.session_state.analysis_cache:
        return st.session_state.analysis_cache[input_hash]
    
    model = initialize_gemini_client()
    if not model:
        return None
    
    # 系統提示詞
    system_prompt = f"""你是專業職涯顧問。請閱讀【履歷】與【職缺】，並 ONLY 以 JSON 回覆，符合下列 schema：

{{
  "match_score": 整數0-100,
  "confidence": 浮點0-1,
  "match_explanation": "請根據履歷與職缺的比對結果，撰寫一段不超過 3 段的自然語言說明，用來在 UI 呈現匹配度摘要。請使用簡單清楚、人性化的語氣",
  "priorities": [{{"name":字串,"weight":0-1,"explanation":字串}}],
  "matched": [{{"item":字串,"evidence":[字串...]}}],
  "missing": [{{"item":字串,"action":字串}}],
  "advice": {{
    "履歷優化": ["具體的履歷改進建議"],
    "求職信建議": ["可直接複製的段落模板"],
    "技能差距分析": ["缺少技能和學習方向"],
    "面試準備建議": ["潛在問題和回答方向"],
    "作品集建議": ["具體的專案題目和展示建議"]
  }}
}}

重要規則：
- 所有回應文字必須完全使用{detected_language}，不能混合其他語言，不用使用敬語（您）
- match_explanation：請根據履歷與職缺的比對結果，撰寫一段不超過 3 段的自然語言說明，用來在 UI 呈現匹配度摘要。請使用簡單清楚、人性化的語氣
- priorities：必須只從職缺內容中挑出重要關鍵技能，不能包含職缺中未提及的技能！每個技能要包含explanation說明為何得分是這樣。
- matched：標題要是關鍵技能，首字要大寫；內文若有多點，要列點式描述哪裡有符合、排版恰當，不用寫「因此給予怎樣的權重。」
- missing：不用每個都寫「建議行動：在履歷中補充相關經驗」，文字要寫的有邏輯，有頭有尾；標題要寫的是有邏輯的履歷提到的經歷、技能，要讓人看得懂
         - advice：必須包含以下五個類別，每個類別提供具體可執行的建議：
           * 履歷優化：關鍵缺漏技能建議、可加入的具體句子、技能欄排序建議、成就量化建議
           * 求職信建議：開場句模板、中段敘述連結過往經驗、結尾句模板（使用{detected_language}，自然表達，不用敬語，可以用「你」）
           * 技能差距分析：缺少技能、學習方向、免費資源/課程建議
           * 面試準備建議：潛在問題、回答方向、STAR回答框架提示
           * 作品集建議：小專案題目、展示建議
- 僅回 JSON，不要其他文字

特別注意：
1. priorities 中的技能必須是職缺描述中明確提及或要求的技能，不能因為履歷中有相關經驗就加入職缺關鍵技能中！
2. 經驗年數評估規則：
   - 只有當職缺有提到此年數要求才需要考慮此規則
   - 如果職缺要求 X 年經驗，履歷只有 Y 年經驗：
     * Y >= X：給 90-100%（經驗充足或超過要求）
     * Y >= X*0.8：給 70-85%（經驗接近要求）
     * Y >= X*0.6：給 50-70%（經驗不足但可接受）
     * Y < X*0.6：給 30-50%（經驗嚴重不足）
   - 必須在 explanation 中明確說明年數差距對分數的影響
3. 技能匹配評估規則：
   - 履歷明確提到相關經驗：給 70-90%
   - 履歷有相關但描述較少：給 50-70%
   - 履歷沒有明確提到：給 20-40%
   - 不要過於保守，如果履歷中有相關經驗就應該給合理的高分
   - 重要：如果履歷明確提到相關經驗，絕對不能給低分（10-30%）！必須給合理的高分！

一致性要求：
- 相同的履歷和職缺描述必須產生相同的分數和評估結果
- 使用結構化的評估標準，避免主觀判斷
- 優先考慮客觀指標（年數、技能匹配度）而非主觀感受
- 嚴格遵守語言一致性：所有回應必須完全使用{detected_language}，不能出現任何其他語言"""

    user_prompt = f"""
履歷內容：
{resume_text}

職缺描述：
{job_description}

請分析匹配度並提供建議。
"""

    try:
        # 創建完整的提示詞
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # 使用 Gemini 生成回應
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # 降低溫度以提高一致性
                max_output_tokens=4000,  # 增加 token 限制以避免截斷
                top_p=0.8,  # 限制詞彙選擇範圍
                top_k=20,   # 限制候選詞數量
            )
        )
        
        response_text = response.text
        
        # 嘗試解析 JSON
        try:
            # 檢查回應是否為空
            if not response_text or response_text.strip() == "":
                st.error("❌ AI 回應為空，請檢查 API 設置")
                return None
            
            # 清理回應文本，提取 JSON 部分
            json_text = ""
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                if json_end > json_start:
                    json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                json_text = response_text.strip()
            
            # 清理無效的控制字符
            import re
            # 移除或替換無效的控制字符（除了 \n, \r, \t）
            json_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', json_text)
            # 確保引號正確配對
            json_text = json_text.replace('"', '"').replace('"', '"')
            json_text = json_text.replace(''', "'").replace(''', "'")
            
            # 檢查提取的 JSON 是否為空
            if not json_text:
                st.error("❌ 無法從 AI 回應中提取 JSON 內容")
                st.text("原始回應:")
                st.text(response_text)
                return None
            
            # 檢查 JSON 是否被截斷
            if json_text.count("{") != json_text.count("}"):
                st.warning("⚠️ JSON 回應可能被截斷，嘗試修復...")
                # 嘗試修復截斷的 JSON
                if json_text.count("{") > json_text.count("}"):
                    # 缺少右括號，嘗試補全
                    missing_braces = json_text.count("{") - json_text.count("}")
                    # 簡單補全：添加缺失的右括號
                    json_text += "}" * missing_braces
                    # 如果最後一個字符不是 }，添加一個
                    if not json_text.endswith("}"):
                        json_text += "}"
                else:
                    # 多餘的右括號，移除
                    extra_braces = json_text.count("}") - json_text.count("{")
                    for _ in range(extra_braces):
                        json_text = json_text.rsplit("}", 1)[0]
            
            # 如果 JSON 仍然不完整，嘗試添加基本的結束結構
            if not json_text.strip().endswith("}"):
                # 檢查是否缺少基本的結束結構
                if '"advice"' in json_text and not json_text.strip().endswith("}"):
                    # 嘗試添加基本的結束結構
                    json_text = json_text.rstrip() + '}}'
                elif '"missing"' in json_text and not json_text.strip().endswith("}"):
                    json_text = json_text.rstrip() + '}'
                elif '"matched"' in json_text and not json_text.strip().endswith("}"):
                    json_text = json_text.rstrip() + '}'
                elif '"priorities"' in json_text and not json_text.strip().endswith("}"):
                    # 如果截斷在 priorities 部分，嘗試補全
                    if json_text.count("[") > json_text.count("]"):
                        json_text = json_text.rstrip() + ']'
                    json_text = json_text.rstrip() + '}'
            
            result = json.loads(json_text)
            # 將檢測到的語言添加到結果中
            result['detected_language'] = detected_language
            # 將結果存入緩存
            st.session_state.analysis_cache[input_hash] = result
            return result
            
        except json.JSONDecodeError as e:
            st.error(f"❌ JSON 解析失敗: {str(e)}")
            st.text("提取的 JSON 文本:")
            st.text(json_text)
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
    match_explanation = result.get('match_explanation', '')
    
    # 根據語言調整字體大小
    font_size = "0.9rem" if language == "English" else "0.85rem"
    
    st.markdown(f"""
    <div class="score-container">
        <h1 class="score-number">{match_score}%</h1>
        <p class="score-label">{texts['match_score_label']}</p>
        <p style="font-size: {font_size}; margin-top: 0.5rem; opacity: 0.8;">{match_explanation}</p>
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
                explanation = priority.get('explanation', '')
                weight_percent = int(weight * 100)
                color = "#28a745" if weight >= 0.7 else "#ffc107" if weight >= 0.5 else "#dc3545"
                
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 0.8rem; margin: 0.3rem 0; border-radius: 6px; 
                           border-left: 3px solid {color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                        <span style="font-weight: 500;">{i}. {name}</span>
                        <span style="font-weight: bold; color: {color};">{weight_percent}%</span>
                    </div>
                    <small style="color: #666; font-size: 0.8rem;">{explanation}</small>
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
                    evidence_list = item['evidence']
                    evidence_html = "<ul style='margin: 0.3rem 0; padding-left: 1.2rem;'>"
                    for evidence in evidence_list:
                        evidence_html += f"<li style='margin: 0.2rem 0;'>{evidence}</li>"
                    evidence_html += "</ul>"
                    st.markdown(f'''
                    <div class="matched-item">
                        <strong>{item["item"]}</strong>
                        {evidence_html}
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
                        <span style="color: #666;">{item["action"]}</span>
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
        st.markdown(f"<div style='font-size: 1.5rem; font-weight: 600; margin: 1.5rem 0 1rem 0; color: #1a1a1a;'>{texts['advice_title']}</div>", unsafe_allow_html=True)
        
        advice_content = result['advice']
        
        # 處理新格式（帶標題的物件）或舊格式
        if isinstance(advice_content, dict):
            advice_html = ""
            
            # 定義每個類別的顏色和翻譯映射
            advice_config = {
                "履歷優化": {"color": "#dc3545", "key": "advice_resume_optimization"},
                "求職信建議": {"color": "#007bff", "key": "advice_cover_letter"},
                "技能差距分析": {"color": "#28a745", "key": "advice_skill_gap"},
                "面試準備建議": {"color": "#6f42c1", "key": "advice_interview"},
                "作品集建議": {"color": "#fd7e14", "key": "advice_portfolio"},
                "Resume Optimization": {"color": "#dc3545", "key": "advice_resume_optimization"},
                "Cover Letter Suggestions": {"color": "#007bff", "key": "advice_cover_letter"},
                "Skill Gap Analysis": {"color": "#28a745", "key": "advice_skill_gap"},
                "Interview Preparation": {"color": "#6f42c1", "key": "advice_interview"},
                "Portfolio Suggestions": {"color": "#fd7e14", "key": "advice_portfolio"}
            }
            
            for title, items in advice_content.items():
                if items and len(items) > 0:
                    config = advice_config.get(title, {"color": "#666"})
                    color = config["color"]
                    
                    # 使用翻譯後的標題，如果沒有找到則使用原始標題
                    display_title = texts.get(config.get("key", ""), title)
                    
                    advice_html += f"<div style='color: {color}; margin-top: 0.8rem; margin-bottom: 0.5rem; font-size: 1.5rem; font-weight: 600;'>{display_title}</div><ul style='margin-bottom: 1rem;'>"
                    for item in items:
                        # 將 **文字** 轉換為 <strong>文字</strong>
                        import re
                        clean_item = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', item)
                        # 清理其他 Markdown 格式
                        clean_item = clean_item.replace("*", "").strip()
                        advice_html += f"<li style='margin: 0.5rem 0; line-height: 1.6;'>{clean_item}</li>"
                    advice_html += "</ul>"
        elif isinstance(advice_content, str):
            # 字符串格式：直接顯示
            advice_html = advice_content
        elif isinstance(advice_content, list):
            advice_html = "<ul>"
            for item in advice_content:
                advice_html += f"<li>{item}</li>"
            advice_html += "</ul>"
        else:
            advice_html = str(advice_content)
        
        st.markdown(f'<div class="advice-box">{advice_html}</div>', unsafe_allow_html=True)

def main():
    # 語言選擇（放在頁面左上角）
    col1, col2 = st.columns([1, 4])
    with col1:
        # 根據瀏覽器語言自動選擇預設語言
        default_lang_index = 0  # 預設中文
        language = st.selectbox("語言 / Language", ["中文", "English"], index=default_lang_index)
    
    # 根據選擇的語言獲取文字
    texts = get_ui_texts(language)
    
    # 主標題
    st.markdown(f'<h1 class="main-header">{texts["app_title"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{texts["app_subtitle"]}</p>', unsafe_allow_html=True)
    
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
            # 使用檢測到的語言來顯示結果和 UI
            display_language = result.get('detected_language', language)
            display_texts = get_ui_texts(display_language)
            st.success(display_texts['analysis_complete'])
            display_results(result, display_language)
            
            # 重新分析按鈕
            st.markdown("<br>", unsafe_allow_html=True)
            col_new1, col_new2, col_new3 = st.columns([1, 2, 1])
            with col_new2:
                if st.button(display_texts['analyze_another'], use_container_width=True):
                    st.rerun()
        else:
            st.error(texts['analysis_failed'])

if __name__ == "__main__":
    main()
    
    # 添加 JavaScript 來處理語言偵測
    st.markdown("""
    <script>
    // 立即執行和延遲執行結合
    function setLanguage() {
        const browserLang = navigator.language || navigator.userLanguage;
        const isChinese = browserLang.startsWith('zh');
        
        // 嘗試多種選擇器
        const selectors = [
            '[data-testid="stSelectbox"] select',
            'select[aria-label*="語言"]',
            'select[aria-label*="Language"]',
            '.stSelectbox select'
        ];
        
        for (const selector of selectors) {
            const selectbox = document.querySelector(selector);
            if (selectbox) {
                // 根據瀏覽器語言設置預設選擇
                if (isChinese) {
                    selectbox.selectedIndex = 0; // 中文
                } else {
                    selectbox.selectedIndex = 1; // 英文
                }
                selectbox.dispatchEvent(new Event('change', { bubbles: true }));
                selectbox.dispatchEvent(new Event('input', { bubbles: true }));
                break;
            }
        }
    }
    
    // 立即執行
    setLanguage();
    
    // 頁面加載完成後執行
    window.addEventListener('load', function() {
        setLanguage();
        setTimeout(setLanguage, 100);
        setTimeout(setLanguage, 500);
        setTimeout(setLanguage, 1000);
    });
    
    // DOM 內容加載完成後也執行
    document.addEventListener('DOMContentLoaded', function() {
        setLanguage();
        setTimeout(setLanguage, 100);
    });
    
    // 監聽 Streamlit 的狀態變化
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                setTimeout(setLanguage, 100);
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    </script>
    """, unsafe_allow_html=True)
