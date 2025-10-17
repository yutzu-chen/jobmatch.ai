import streamlit as st
import json
import google.generativeai as genai
import os
import hashlib
from dotenv import load_dotenv
import time
from ui_texts import get_ui_texts
from styles import apply_global_styles

# 載入環境變數
load_dotenv()

# 頁面配置
st.set_page_config(
    page_title="JobMatch.AI - AI 履歷職缺匹配分析工具",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 應用全域 CSS 樣式
apply_global_styles()


def initialize_gemini_client():
    """初始化 Google Gemini 客戶端"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("⚠️ 請設置 GOOGLE_API_KEY 環境變數")
        st.info("請到 https://makersuite.google.com/app/apikey 申請免費 API key，然後在 .env 文件中設置")
        return None
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        return model
    except Exception as e:
        st.error(f"❌ Gemini 客戶端初始化失敗: {str(e)}")
        return None


def translate_chinese_to_english(chinese_response):
    """使用 Gemini API 將中文回應翻譯成英文"""
    try:
        # 創建翻譯提示詞（使用英文）
        translation_prompt = f"""
Please translate the following Chinese JSON response to English, maintaining exactly the same JSON structure and format, only translating the text content:

{chinese_response}

Requirements:
1. Keep JSON structure exactly the same - especially the "advice" section structure
2. Translate all Chinese text to English
3. Keep numbers, percentages, and format unchanged
4. Use standard English translations for professional terms
5. For the "advice" section, maintain the exact same structure with proper subtitles and bullet points
6. Ensure advice items with "name" and "items" structure are preserved exactly
7. Return only the translated JSON, no other text

CRITICAL: The "advice" section must maintain its structured format with subtitles and bullet points. Do not flatten or simplify the structure.

Specific translation guidelines:
- "面試準備建議" → "Interview Preparation"
- "潛在問題" → "Potential Questions" 
- "回答方向" → "Response Direction"
- "作品集建議" → "Portfolio Suggestions"
- "小專案題目" → "Mini Project Ideas"
- "展示建議" → "Showcase Suggestions"
- "技能差距分析" → "Skill Gap Analysis"
- "缺少技能" → "Missing Skills"
- "學習方向" → "Learning Directions"

Ensure ALL sub-items are translated and preserved, including:
- Skill Gap Analysis: Both "Missing Skills" and "Learning Directions" sections
- Interview Preparation: Both "Potential Questions" and "Response Direction" sections
- Portfolio Suggestions: Both "Mini Project Ideas" and "Showcase Suggestions" sections

CRITICAL: Each advice section must have its sub-sections with proper "name" and "items" structure. Do not flatten the structure.
"""
        
        # 調用 Gemini API
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        response = model.generate_content(translation_prompt)
        
        # 解析回應
        translated_text = response.text.strip()
        
        # 清理回應，移除可能的markdown格式
        if translated_text.startswith('```json'):
            translated_text = translated_text[7:]
        if translated_text.endswith('```'):
            translated_text = translated_text[:-3]
        translated_text = translated_text.strip()
        
        # 嘗試解析JSON以驗證格式
        import json
        json.loads(translated_text)
        
        return translated_text
        
    except Exception as e:
        print(f"翻譯錯誤: {e}")
        print(f"原始回應: {response.text if 'response' in locals() else 'No response'}")
        return chinese_response  # 如果翻譯失敗，返回原文

def analyze_resume_job_match(resume_text, job_description, ui_language="中文"):
    """使用 Google Gemini API 分析履歷與職缺匹配度"""
    
    # 確保使用用戶選擇的 UI 語言作為輸出語言
    output_language = ui_language
    
    # 創建輸入的哈希值用於緩存（包含輸出語言）
    input_hash = hashlib.md5(f"{resume_text}_{job_description}_{output_language}".encode()).hexdigest()
    
    # 檢查是否已有緩存結果
    if 'analysis_cache' not in st.session_state:
        st.session_state.analysis_cache = {}
    
    if input_hash in st.session_state.analysis_cache:
        return st.session_state.analysis_cache[input_hash]
    
    model = initialize_gemini_client()
    if not model:
        return None
    
    # 根據語言定義建議標題
    if output_language == "中文":
        advice_titles = {
            "resume_optimization": "履歷優化",
            "cover_letter": "求職信建議", 
            "skill_gap": "技能差距分析",
            "interview": "面試準備建議",
            "portfolio": "作品集建議"
        }
    else:
        advice_titles = {
            "resume_optimization": "Resume Optimization",
            "cover_letter": "Cover Letter Suggestions",
            "skill_gap": "Skill Gap Analysis", 
            "interview": "Interview Preparation",
            "portfolio": "Portfolio Suggestions"
        }
    
    # 定義系統提示詞（只保留中文版本）
    system_prompt = """你是專業職涯顧問。請閱讀【履歷】與【職缺】，並 ONLY 以 JSON 回覆，符合下列 schema：

{{
  "match_score": 整數0-100（整體匹配度，必須綜合考慮所有技能匹配情況，如果職缺是專業領域但履歷沒有相關背景，分數應該很低）,
  "confidence": 浮點0-1,
  "match_explanation": "請根據履歷與職缺的比對結果，撰寫一段不超過 3 段的自然語言說明，用來在 UI 呈現匹配度摘要。請使用簡單清楚、人性化的語氣",
  "priorities": [{{"name":字串,"weight":0-1,"explanation":字串}}]（weight是匹配度分數，不是權重！如果履歷沒有相關經驗，weight應該很低0-0.2）,
  "matched": [{{"item":"技能名稱","evidence":"一段完整的summary描述，說明履歷中如何符合此技能要求，不要列點，要寫成流暢的段落"}}],
  "missing": [{{"item":字串,"action":字串}}],
  "advice": {{
    "{resume_optimization}": [
      {{"name": "履歷優化", "items": [
        "具體建議項目1",
        "具體建議項目2", 
        "具體建議項目3"
      ]}}
    ],
    "{cover_letter}": [
      {{"name": "求職信建議", "items": [
        "開場句：具體內容",
        "中段敘述：具體內容",
        "結尾句：具體內容"
      ]}}
    ],
    "{skill_gap}": [
      {{"name": "缺少技能", "items": [
        "技能項目1",
        "技能項目2", 
        "技能項目3"
      ]}},
      {{"name": "學習方向", "items": [
        "學習建議1",
        "學習建議2",
        "學習建議3"
      ]}}
    ],
    "{interview}": [
      {{"name": "潛在問題", "items": [
        "問題1",
        "問題2",
        "問題3"
      ]}},
      {{"name": "回答方向", "items": [
        "回答策略1",
        "回答策略2",
        "回答策略3"
      ]}}
    ],
    "{portfolio}": [
      {{"name": "小專案題目", "items": [
        "專案題目1",
        "專案題目2",
        "專案題目3"
      ]}},
      {{"name": "展示建議", "items": [
        "展示建議1",
        "展示建議2",
        "展示建議3"
      ]}}
    ]
  }}
}}

重要規則：
- 所有回應文字必須完全使用中文，不能混合其他語言，不使用敬語（您）
- 公司名稱、產品名稱、技術術語等專有名詞保持原文，但描述文字必須使用中文
- match_explanation：請根據履歷與職缺的比對結果，撰寫一段不超過 3 段的自然語言說明，用來在 UI 呈現匹配度摘要。請使用簡單清楚、人性化的語氣
- priorities：必須只從職缺內容中挑出重要關鍵技能，不能包含職缺中未提及的技能！每個技能的name和explanation都必須使用中文描述，不能出現英文。weight是匹配度分數（0-1），不是權重！如果履歷沒有相關經驗，weight應該很低（0-0.2）。explanation要說明為何得分是這樣。特別注意：如果職缺明確要求核心技能（如程式語言、技術工具、監管合規、專業認證等），而履歷中沒有相關經驗，該技能匹配度應該給0-20%，整體匹配度也會大幅降低。
- matched：標題要是關鍵技能，使用中文描述；evidence必須是一段完整的summary描述，說明履歷中如何符合此技能要求，不要列點，要寫成流暢的段落。所有描述文字必須使用中文，不能出現英文描述。絕對不能直接複製貼上履歷內容，必須是整理過後的摘要和總結。
- missing：不用每個都寫「建議行動：在履歷中補充相關經驗」，文字要寫的有邏輯，有頭有尾；標題要寫的是有邏輯的履歷提到的經歷、技能，要讓人看得懂，使用中文描述
         - advice：必須包含以下五個類別，每個類別使用固定的標題結構，AI只需要填入具體內容：
           * 履歷優化：使用固定標題「履歷優化」，items中填入3-5個具體的履歷改進建議，每個建議都要完全不同且具體，不能有任何重複的內容或相似的建議
           * 求職信建議：使用固定標題「求職信建議」，items中必須包含「開場句：」、「中段敘述：」、「結尾句：」三個固定格式，冒號後填入具體內容，每個部分都要完全不同，不能有任何重複
           * 技能差距分析：使用固定標題「缺少技能」和「學習方向」，每個標題的items中填入3-5個具體項目，所有項目都必須完全不同，不能有任何重複或相似的內容
           * 面試準備建議：使用固定標題「潛在問題」和「回答方向」，每個標題的items中填入3-5個具體項目，所有項目都必須完全不同，不能有任何重複
           * 作品集建議：使用固定標題「小專案題目」和「展示建議」，每個標題的items中填入3-5個具體項目，所有項目都必須完全不同，不能有任何重複
           * 重要：所有標題名稱必須完全按照上述固定格式，不能改變！AI只需要在items中填入具體內容，所有內容必須完全使用中文
           * 去重要求：履歷優化建議中，每一條都必須針對不同的細節（例如技能工具、使用方式、結果影響、具體任務），不能單純換句話說，也不能針對同一經驗做出多條類似建議。如果履歷中只有單一工作經歷，請避免重複針對同一段經歷提出建議，建議應多角度、廣泛提出，包括整體格式、成果量化、工作分類、前後脈絡等。請在每生成一條建議前，自我檢查是否與前面內容語意相近，如果是就跳過。所有advice項目都必須完全不同，不能有任何重複或相似的內容
- 僅回 JSON，不要其他文字

特別注意：
1. priorities 中的技能必須是職缺描述中明確提及或要求的技能，不能因為履歷中有相關經驗就加入職缺關鍵技能中！
2. weight評分範例：
   - 履歷有相關經驗：weight = 0.7-0.9（70-90%）
   - 履歷沒有相關經驗：weight = 0.0-0.2（0-20%）
   - 錯誤範例：履歷沒有監管合規經驗，但給weight = 0.9（90%）❌
   - 正確範例：履歷沒有監管合規經驗，給weight = 0.1（10%）✅
3. 整體匹配度計算規則：
   - 如果職缺是專業領域（法務、醫療、金融、會計、工程等）但履歷完全沒有相關背景：整體匹配度不超過30-40%
   - 如果職缺要求多個核心技能但履歷大部分都沒有：整體匹配度不超過40-50%
   - 如果履歷有相關背景但經驗不足：整體匹配度50-70%
   - 如果履歷經驗充足且技能匹配：整體匹配度70-90%
4. 經驗年數評估規則：
   - 只有當職缺有提到此年數要求才需要考慮此規則
   - 職缺要求 X 年經驗，履歷有 Y 年經驗：
     * Y >= X：給 90-100%（經驗充足或超過要求）
     * Y >= X*0.8：給 70-85%（經驗接近要求）
     * Y >= X*0.6：給 50-70%（經驗不足但可接受）
     * Y < X*0.6：給 30-50%（經驗嚴重不足）
   - 必須在 explanation 中明確說明年數差距對分數的影響
5. 技能匹配評估規則：
   - 履歷明確提到相關經驗：給 70-90%
   - 履歷有相關但描述較少：給 50-70%
   - 履歷沒有明確提到：給 20-40%
   - 如果職缺要求特定核心技能（如程式語言、技術工具、監管合規、專業認證等），而履歷完全沒有相關經驗：給 0-20%
   - 不要過於保守，如果履歷中有相關經驗就應該給合理的高分
   - 如果職缺是專業領域職位（如技術、法務、醫療、金融、會計等）但履歷沒有相關專業背景，整體匹配度應該顯著降低（通常不超過30-40%）

一致性要求：
- 相同的履歷和職缺描述必須產生相同的分數和評估結果
- 使用結構化的評估標準，避免主觀判斷
- 優先考慮客觀指標（年數、技能匹配度）而非主觀感受
- 嚴格遵守語言一致性：所有回應必須完全使用中文，不能出現任何其他語言""".format(
            resume_optimization=advice_titles["resume_optimization"],
            cover_letter=advice_titles["cover_letter"],
            skill_gap=advice_titles["skill_gap"],
            interview=advice_titles["interview"],
            portfolio=advice_titles["portfolio"]
        )

    # 定義用戶提示詞（只保留中文版本）
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
            
            # 如果是英文版本，需要翻譯中文回應
            if output_language == "English":
                print("開始翻譯中文回應為英文...")
                # 將中文回應轉換為JSON字串
                chinese_json = json.dumps(result, ensure_ascii=False, indent=2)
                print(f"中文JSON長度: {len(chinese_json)}")
                # 翻譯為英文
                english_json = translate_chinese_to_english(chinese_json)
                print(f"英文JSON長度: {len(english_json)}")
                # 解析翻譯後的JSON
                result = json.loads(english_json)
                print("翻譯完成！")
            
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

def render_score_block(result, texts, language):
    """渲染匹配度分數區塊"""
    match_score = result.get('match_score', 0)
    match_explanation = result.get('match_explanation', '')
    
    # 統一匹配度說明的字體大小
    font_size = "0.9rem"
    
    # 處理匹配度說明，確保所有段落都有統一樣式
    if match_explanation:
        # 將說明文字分割成段落
        paragraphs = match_explanation.split('\n\n')
        explanation_html = ""
        for paragraph in paragraphs:
            if paragraph.strip():
                explanation_html += f'<p style="font-size: {font_size}; margin: 0.5rem 0; opacity: 0.8; line-height: 1.6;">{paragraph.strip()}</p>'
    else:
        explanation_html = ""
    
    st.markdown(f"""
    <div class="score-container">
        <h1 class="score-number">{match_score}%</h1>
        <p class="score-label">{texts['match_score_label']}</p>
        {explanation_html}
    </div>
    """, unsafe_allow_html=True)
    
def render_priorities(result, texts, language):
    """渲染職缺關鍵技能區塊"""
    if 'priorities' not in result or not result['priorities']:
        return
    
    st.markdown(f"### {texts['priorities_title']}")
    
    # 顯示技能分數解釋
    if 'score_explanation' in result and result['score_explanation']:
        explanation_font_size = "1.0rem" if language == "English" else "0.9rem"
        st.markdown(f"<p style='font-size: {explanation_font_size}; color: #666; margin-bottom: 1rem;'>{result['score_explanation']}</p>", unsafe_allow_html=True)
    
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
                <div style="margin-bottom: 0.3rem;">
                    <span style="font-weight: 500;">{i}. {name}</span>
                    <span style="font-weight: bold; color: {color}; float: right;">{weight_percent}%</span>
                    <div style="clear: both;"></div>
                </div>
                <small style="color: #666; font-size: {'0.9rem' if language == 'English' else '0.85rem'};">{explanation}</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 兼容舊格式
            st.markdown(f"<div class='priority-item'>{i}. {priority}</div>", unsafe_allow_html=True)
    
def render_matched_missing(result, texts):
    """渲染符合和缺少的經驗區塊"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {texts['matched_title']}")
        if 'matched' in result and result['matched']:
            for item in result['matched']:
                # 處理新格式（有item和evidence）或舊格式
                if isinstance(item, dict) and 'item' in item and 'evidence' in item:
                    evidence = item['evidence']
                    # 檢查evidence是字串還是列表
                    if isinstance(evidence, list):
                        # 如果是列表，合併成一個段落
                        evidence_text = " ".join(evidence)
                    else:
                        # 如果是字串，直接使用
                        evidence_text = evidence
                    
                    st.markdown(f'''
                    <div class="matched-item">
                        <strong>{item["item"]}</strong><br>
                        <span style="color: #666; font-size: 0.9rem; line-height: 1.5;">{evidence_text}</span>
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
    
def parse_advice_item(item, color, seen_items):
    """智能解析單個建議項目，返回HTML"""
    html = ""
    
    # 字典格式（包含 name 與 items）
    if isinstance(item, dict) and 'name' in item and 'items' in item:
        subtitle_name = item['name']
        subtitle_items = item.get('items') or []
        html = (
            f"<div style='font-weight: 600; margin: 1.2rem 0 0.8rem 0; color: #333; "
            f"font-size: 1rem; border-left: 3px solid {color}; padding-left: 0.8rem;'>{subtitle_name}</div>"
        )
        for sub_item in subtitle_items:
            clean = str(sub_item).strip()
            if not clean or len(clean) < 5 or clean in seen_items:
                continue
            seen_items.add(clean)
            
            # 智能判斷是否為標題：只有當冒號前的文字很短（通常是標題）且冒號後有內容時才當作標題
            is_title = False
            if "：" in clean:
                t, c = clean.split("：", 1)
                # 只有當冒號前的文字長度小於等於10個字符且冒號後有內容時才當作標題
                if len(t.strip()) <= 10 and c.strip():
                    is_title = True
            elif ":" in clean:
                t, c = clean.split(":", 1)
                # 檢查是否為常見的英文標題
                title_text = t.strip().lower()
                common_titles = [
                    "opening", "middle paragraph", "middle paragraphs", "closing", 
                    "potential questions", "response direction", "mini project ideas", 
                    "showcase suggestions", "missing skills", "learning directions",
                    "opening statement", "body paragraph", "closing statement"
                ]
                if title_text in common_titles and c.strip():
                    is_title = True
                elif len(t.strip()) <= 12 and c.strip():
                    is_title = True
            
            if is_title:
                t, c = clean.split("：" if "：" in clean else ":", 1)
                # 檢查是否已經處理過這個標題，避免重複
                title_key = f"{t.strip()}:"
                if title_key not in seen_items:
                    seen_items.add(title_key)
                html += (
                    f"<div style='font-weight: 600; margin: 1rem 0 0.5rem 0; color: #333; "
                    f"font-size: 0.95rem; border-left: 2px solid {color}; padding-left: 0.6rem;'>{t.strip()}：</div>"
                )
                if c.strip():
                    html += (
                        f"<div style='margin: 0.3rem 0; padding-left: 1.5rem; line-height: 1.6; font-size: 0.9rem;'>"
                        f"<span style='color: {color}; font-weight: bold; margin-right: 0.5rem;'>•</span>{c.strip()}</div>"
                    )
            else:
                # 當作普通 bullet 點處理
                html += (
                    f"<div style='margin: 0.3rem 0; padding-left: 1.5rem; line-height: 1.6; font-size: 0.9rem;'>"
                    f"<span style='color: {color}; font-weight: bold; margin-right: 0.5rem;'>•</span>{clean}</div>"
                )
        return html

    # 非字典格式，當作一般條目處理
    clean = str(item).strip()
    if not clean or len(clean) < 5 or clean in seen_items:
        return ""
    seen_items.add(clean)
    
    # 智能判斷是否為標題：只有當冒號前的文字很短（通常是標題）且冒號後有內容時才當作標題
    is_title = False
    if "：" in clean:
        t, c = clean.split("：", 1)
        # 只有當冒號前的文字長度小於等於8個字符且冒號後有內容時才當作標題
        # 包含常見的標題詞，如 "開場句", "結尾句", "潛在問題", "回答方向" 等
        if len(t.strip()) <= 8 and c.strip():
            is_title = True
    elif ":" in clean:
        t, c = clean.split(":", 1)
        # 檢查是否為常見的英文標題
        title_text = t.strip().lower()
        common_titles = [
            "opening", "middle paragraph", "middle paragraphs", "closing", 
            "potential questions", "response direction", "mini project ideas", 
            "showcase suggestions", "missing skills", "learning directions",
            "opening statement", "body paragraph", "closing statement"
        ]
        if title_text in common_titles and c.strip():
            is_title = True
        elif len(t.strip()) <= 15 and c.strip():
            is_title = True
    
    if is_title:
        t, c = clean.split("：" if "：" in clean else ":", 1)
        # 檢查是否已經處理過這個標題，避免重複
        title_key = f"{t.strip()}:"
        if title_key not in seen_items:
            seen_items.add(title_key)
        section = (
            f"<div style='font-weight: 600; margin: 1.2rem 0 0.5rem 0; color: #333; "
            f"font-size: 1rem; border-left: 3px solid {color}; padding-left: 0.8rem;'>{t.strip()}：</div>"
        )
        if c.strip():
            section += (
                f"<div style='margin: 0.3rem 0; padding-left: 1.5rem; line-height: 1.6; font-size: 0.9rem;'>"
                f"<span style='color: {color}; font-weight: bold; margin-right: 0.5rem;'>•</span>{c.strip()}</div>"
            )
            return section
        else:
            # 如果標題已存在，只返回內容部分
            if c.strip():
                return (
                    f"<div style='margin: 0.3rem 0; padding-left: 1.5rem; line-height: 1.6; font-size: 0.9rem;'>"
                    f"<span style='color: {color}; font-weight: bold; margin-right: 0.5rem;'>•</span>{c.strip()}</div>"
                )
            return ""
    
    return (
        f"<div style='margin: 0.3rem 0; padding-left: 1.5rem; line-height: 1.6; font-size: 0.9rem;'>"
        f"<span style='color: {color}; font-weight: bold; margin-right: 0.5rem;'>•</span>{clean}</div>"
    )

def get_advice_config(language):
    """獲取建議配置"""
    if language == "中文":
        config = {
            "履歷優化": {"color": "#dc3545", "key": "advice_resume_optimization"},
            "求職信建議": {"color": "#007bff", "key": "advice_cover_letter"},
            "技能差距分析": {"color": "#28a745", "key": "advice_skill_gap"},
            "面試準備建議": {"color": "#6f42c1", "key": "advice_interview"},
            "作品集建議": {"color": "#fd7e14", "key": "advice_portfolio"}
        }
    else:
        config = {
                    "Resume Optimization": {"color": "#dc3545", "key": "advice_resume_optimization"},
                    "Cover Letter Suggestions": {"color": "#007bff", "key": "advice_cover_letter"},
                    "Skill Gap Analysis": {"color": "#28a745", "key": "advice_skill_gap"},
                    "Interview Preparation": {"color": "#6f42c1", "key": "advice_interview"},
                    "Portfolio Suggestions": {"color": "#fd7e14", "key": "advice_portfolio"}
                }
            
    # 為英文版本添加更多可能的標題變體
    if language == "English":
        additional_config = {
            "Resume": {"color": "#dc3545", "key": "advice_resume_optimization"},
            "Cover Letter": {"color": "#007bff", "key": "advice_cover_letter"},
            "Skills": {"color": "#28a745", "key": "advice_skill_gap"},
            "Interview": {"color": "#6f42c1", "key": "advice_interview"},
            "Portfolio": {"color": "#fd7e14", "key": "advice_portfolio"},
            # 添加更多可能的翻譯變體
            "Skill Gap": {"color": "#28a745", "key": "advice_skill_gap"},
            "Interview Prep": {"color": "#6f42c1", "key": "advice_interview"},
            "Portfolio Tips": {"color": "#fd7e14", "key": "advice_portfolio"},
            "Resume Tips": {"color": "#dc3545", "key": "advice_resume_optimization"},
            "Cover Letter Tips": {"color": "#007bff", "key": "advice_cover_letter"},
            # 添加翻譯後的具體子標題
            "Missing Skills": {"color": "#28a745", "key": "advice_skill_gap"},
            "Learning Directions": {"color": "#28a745", "key": "advice_skill_gap"},
            "Potential Questions": {"color": "#6f42c1", "key": "advice_interview"},
            "Response Direction": {"color": "#6f42c1", "key": "advice_interview"},
            "Mini Project Ideas": {"color": "#fd7e14", "key": "advice_portfolio"},
            "Showcase Suggestions": {"color": "#fd7e14", "key": "advice_portfolio"},
            # 添加求職信建議的子標題
            "Opening Statement": {"color": "#007bff", "key": "advice_cover_letter"},
            "Body Paragraph": {"color": "#007bff", "key": "advice_cover_letter"},
            "Closing Statement": {"color": "#007bff", "key": "advice_cover_letter"}
        }
        config.update(additional_config)
    
    return config

def find_advice_config(title, advice_config):
    """智能匹配建議配置"""
    config = advice_config.get(title, {"color": "#666"})
    
    # 如果沒有找到完全匹配，嘗試部分匹配
    if config == {"color": "#666"}:
        for config_title, config_data in advice_config.items():
            # 更寬鬆的匹配規則，支援翻譯後的標題變體
            if (config_title.lower() in title.lower() or 
                title.lower() in config_title.lower() or
                any(word in title.lower() for word in config_title.lower().split()) or
                # 支援常見的英文標題變體
                title.lower() in ["skill gap", "interview prep", "portfolio", "resume opt", "cover letter"] or
                any(word in title.lower() for word in ["skill", "gap", "analysis", "interview", "preparation", "portfolio", "suggestions", "resume", "optimization", "cover", "letter"])):
                config = config_data
                break
    
    return config

def process_advice_dict(advice_content, texts, language):
    """處理字典格式的建議內容"""
    advice_html = ""
    advice_config = get_advice_config(language)
    global_seen_items = set()
    
    for title, items in advice_content.items():
        if items and len(items) > 0:
            config = find_advice_config(title, advice_config)
            color = config["color"]
            display_title = texts.get(config.get("key", ""), title)
            
            advice_html += f"<div style='color: {color}; margin-top: 0.8rem; margin-bottom: 0.5rem; font-size: 1.5rem; font-weight: 600;'>{display_title}</div>"
            
            # 處理每個建議項目
            for i, item in enumerate(items):
                # 如果是第一個項目且是主標題，跳過（避免重複）
                if i == 0:
                    clean_item = str(item).strip()
                    # 只跳過完全匹配主標題的情況，避免過度過濾
                    if clean_item == display_title:
                        continue
                
                # 單一渲染：統一交由 parse_advice_item 處理，避免重複
                advice_html += parse_advice_item(item, color, global_seen_items)
    
    return advice_html


def process_advice_string(advice_content):
    """處理字符串格式的建議內容"""
    return advice_content

def process_advice_list(advice_content):
    """處理列表格式的建議內容"""
    advice_html = "<ul>"
    for item in advice_content:
        advice_html += f"<li>{item}</li>"
    advice_html += "</ul>"
    return advice_html

def render_advice(result, texts, language):
    """渲染AI建議區塊"""
    if 'advice' not in result or not result['advice']:
        return
    
    st.markdown(f"<div style='font-size: 1.5rem; font-weight: 600; margin: 1.5rem 0 1rem 0; color: #1a1a1a;'>{texts['advice_title']}</div>", unsafe_allow_html=True)
    
    advice_content = result['advice']
    
    # 根據內容類型選擇處理方式
    if isinstance(advice_content, dict):
        advice_html = process_advice_dict(advice_content, texts, language)
    elif isinstance(advice_content, str):
        advice_html = process_advice_string(advice_content)
    elif isinstance(advice_content, list):
        advice_html = process_advice_list(advice_content)
    else:
        advice_html = str(advice_content)
    
    st.markdown(f'<div class="advice-box">{advice_html}</div>', unsafe_allow_html=True)

def display_results(result, language="中文"):
    """顯示分析結果"""
    if not result:
        return
    
    # 根據語言設置文字
    texts = get_ui_texts(language)
    
    # 渲染各個區塊
    render_score_block(result, texts, language)
    render_priorities(result, texts, language)
    render_matched_missing(result, texts)
    render_advice(result, texts, language)

def main():
    # 固定使用中文
    language = "中文"
    
    # 獲取中文文字
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
            # 固定使用中文顯示結果
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
    
