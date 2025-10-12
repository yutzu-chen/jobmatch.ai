# MatchMe.AI 💼 - AI 履歷職缺匹配分析工具

一個使用 AI 分析履歷與職缺匹配度的智能工具，幫助求職者了解自己的優勢和需要改進的地方。

## ✨ 功能特色

- 🤖 **AI 智能分析**: 使用 Groq + Llama 3 70B 模型進行深度分析
- 📊 **匹配度評分**: 0-100 分的精確匹配度評估
- 🎯 **技能優先級**: 識別職缺最重視的技能和特質
- ✅ **優勢分析**: 清楚列出你已具備的經驗
- ⚠️ **改進建議**: 指出需要補強的能力
- 💡 **實用建議**: 提供可直接使用的求職建議
- 🔒 **隱私保護**: 不保存任何個人資料
- 🌍 **多語言支援**: 支援中文、英文、德文分析

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設置 API Key

1. 到 [Groq Console](https://console.groq.com/) 申請免費 API key
2. 複製 `.env.example` 為 `.env`
3. 在 `.env` 文件中設置你的 API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 3. 運行應用

```bash
streamlit run app.py
```

應用將在 `http://localhost:8501` 啟動

## 📱 使用方式

1. **輸入履歷**: 在左側文本框中貼上你的履歷內容
2. **輸入職缺**: 在右側文本框中貼上職缺描述
3. **選擇語言**: 在側邊欄選擇分析語言
4. **開始分析**: 點擊「開始分析匹配度」按鈕
5. **查看結果**: 獲得詳細的匹配度分析和建議

## 🎨 界面預覽

- **匹配度分數**: 大數字顯示 0-100 分匹配度
- **技能優先級**: 條形圖顯示職缺最重視的技能
- **雙欄對比**: 左側顯示符合的經驗，右側顯示缺少的經驗
- **AI 建議**: 提供實用的改進建議

## 🛠️ 技術架構

- **前端**: Streamlit
- **AI 模型**: Groq API + Llama 3 70B
- **部署**: Streamlit Cloud (免費)
- **語言**: Python 3.8+

## 📦 部署到 Streamlit Cloud

1. 將代碼推送到 GitHub 倉庫
2. 到 [Streamlit Cloud](https://share.streamlit.io/) 連接你的倉庫
3. 設置環境變數 `GROQ_API_KEY`
4. 部署完成！

## 🔧 自定義配置

### 修改 AI 模型

在 `app.py` 中修改模型名稱：

```python
model="llama3-70b-8192"  # 可改為其他 Groq 支援的模型
```

### 調整分析語言

在側邊欄的語言選擇中添加更多選項：

```python
language = st.selectbox("分析語言", ["中文", "English", "Deutsch", "Français"], index=0)
```

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License

## 🆘 常見問題

### Q: API key 在哪裡申請？
A: 到 [Groq Console](https://console.groq.com/) 註冊並申請免費 API key

### Q: 分析結果準確嗎？
A: 使用最新的 Llama 3 70B 模型，準確度很高，但建議結合人工判斷

### Q: 支援哪些語言？
A: 目前支援中文、英文、德文，可以輕鬆擴展其他語言

### Q: 資料會被保存嗎？
A: 不會，所有分析都是即時進行，不保存任何個人資料

---

**MatchMe.AI** - 讓 AI 幫你找到理想工作！ 🚀
