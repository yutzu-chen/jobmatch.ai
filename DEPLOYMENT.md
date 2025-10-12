# 🚀 MatchMe.AI 部署指南

## ✅ 本地測試完成

你的 MatchMe.AI 應用已經在本地成功運行！

- ✅ API 連接測試通過
- ✅ Streamlit 應用啟動成功
- ✅ 所有依賴包已安裝

**本地訪問地址**: http://localhost:8501

## 🌐 部署到 Streamlit Cloud

### 步驟 1: 準備 GitHub 倉庫

1. 在 GitHub 創建新倉庫
2. 將所有文件推送到倉庫：

```bash
git init
git add .
git commit -m "Initial commit: MatchMe.AI 履歷職缺匹配分析工具"
git branch -M main
git remote add origin https://github.com/你的用戶名/你的倉庫名.git
git push -u origin main
```

### 步驟 2: 部署到 Streamlit Cloud

1. 訪問 [Streamlit Community Cloud](https://share.streamlit.io/)
2. 使用 GitHub 帳號登入
3. 點擊 "New app"
4. 選擇你的倉庫和分支
5. 設置主文件路徑為 `app.py`
6. 點擊 "Deploy"

### 步驟 3: 設置環境變數

部署完成後：

1. 進入應用的管理頁面
2. 點擊 "Settings" → "Secrets"
3. 添加環境變數：

```
GROQ_API_KEY = 你的實際API_key
```

### 步驟 4: 重新部署

設置環境變數後，應用會自動重新部署。

## 🔧 其他部署選項

### 使用 Heroku

1. 創建 `Procfile`:
```
web: streamlit run app.py --server.port=$PORT
```

2. 創建 `setup.sh`:
```bash
mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
```

3. 部署到 Heroku:
```bash
heroku create your-app-name
git push heroku main
```

### 使用 Docker

創建 `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🎯 部署後檢查清單

- [ ] 應用成功啟動
- [ ] API 連接正常
- [ ] 可以輸入履歷和職缺描述
- [ ] AI 分析功能正常
- [ ] 結果顯示正確
- [ ] 響應速度合理（2-5秒）

## 🆘 常見問題

### Q: 部署後顯示 "API 連接失敗"
A: 檢查環境變數 `GROQ_API_KEY` 是否正確設置

### Q: 應用啟動失敗
A: 檢查 `requirements.txt` 中的依賴版本是否正確

### Q: 分析結果不準確
A: 可以調整 `app.py` 中的 `temperature` 參數（0.1-0.5 更保守，0.5-1.0 更創意）

## 📞 需要幫助？

如果遇到任何問題，請檢查：
1. API key 是否正確
2. 網絡連接是否正常
3. 依賴包版本是否兼容

---

**恭喜！你的 MatchMe.AI 已經準備好上線了！** 🎉
