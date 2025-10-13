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

一个基于 AI 的智能职位匹配工具，帮助求职者分析简历与职位的匹配度。

## 功能特点

- 🤖 使用 Google Gemini AI 进行智能分析
- 🌍 支持中文和英文界面
- 📊 提供匹配度评分和详细分析
- 💼 简洁易用的用户界面

## 使用方法

1. 在左侧输入框中粘贴你的简历内容
2. 在右侧输入框中粘贴职位描述
3. 点击"开始分析"按钮
4. 查看匹配度评分和分析结果

## 环境变量

在 Hugging Face Spaces 中设置以下环境变量：

- `GOOGLE_API_KEY`: 你的 Google AI API 密钥

## 技术栈

- Streamlit: Web 应用框架
- Google Generative AI: AI 分析引擎
- Python: 后端语言

## 许可证

MIT License