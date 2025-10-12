# MatchMe.AI - AI 履歷職缺匹配分析工具

一個使用 AI 分析履歷與職缺匹配度的智能工具，幫助求職者了解自己的優勢和需要改進的地方。

## ✨ 功能特色

- **AI 智能分析**: 使用 Groq + Llama 3.3 70B 模型進行深度分析
- **匹配度評分**: 0-100 分的精確匹配度評估
- **技能優先級**: 識別職缺最重視的技能和特質
- **優勢分析**: 清楚列出你已具備的經驗
- **改進建議**: 指出需要補強的能力
- **多語言支援**: 支援中文、英文、德文分析
- **隱私保護**: 不保存任何個人資料

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設置 API Key

1. 到 [Groq Console](https://console.groq.com/) 申請免費 API key
2. 創建 `.env` 文件並設置：

```
GROQ_API_KEY=your_groq_api_key_here
```

### 3. 運行應用

```bash
streamlit run app.py
```

## 📱 使用方式

1. 在左側貼上你的履歷內容
2. 在右側貼上職缺描述
3. 選擇分析語言
4. 點擊「開始分析匹配度」
5. 查看詳細的匹配度分析和建議

## 🛠️ 技術架構

- **前端**: Streamlit
- **AI 模型**: Groq API + Llama 3.3 70B
- **語言**: Python 3.8+

## 📦 部署

1. 推送到 GitHub 倉庫
2. 到 [Streamlit Cloud](https://share.streamlit.io/) 部署
3. 設置環境變數 `GROQ_API_KEY`

## 📄 授權

MIT License

---

**MatchMe.AI** - 讓 AI 幫你找到理想工作！