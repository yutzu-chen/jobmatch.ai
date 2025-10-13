---
title: JobMatch.AI
emoji: 💼
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
license: mit
short_description: AI-powered job matching tool
---

# JobMatch.AI

一個基於 AI 的智能職位匹配工具，幫助求職者分析履歷與職位的匹配度。

## 功能特點

- 🤖 使用 Google Gemini AI 進行智能分析
- 🌍 支援中文和英文介面
- 📊 提供匹配度評分和詳細分析
- 💼 簡潔易用的使用者介面

## 使用方法

1. 在左側輸入框中貼上你的履歷內容
2. 在右側輸入框中貼上職位描述
3. 點擊「開始分析」按鈕
4. 查看匹配度評分和分析結果

## 環境變數

在 Hugging Face Spaces 中設定以下環境變數：

- `GOOGLE_API_KEY`: 你的 Google AI API 金鑰

## 技術棧

- Streamlit: Web 應用框架
- Google Generative AI: AI 分析引擎
- Python: 後端語言

## 授權

MIT License