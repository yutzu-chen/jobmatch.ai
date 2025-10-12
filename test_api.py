#!/usr/bin/env python3
"""
測試 Groq API 連接的簡單腳本
"""

import os
from dotenv import load_dotenv
from groq import Groq

def test_groq_connection():
    """測試 Groq API 連接"""
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ 錯誤: 請設置 GROQ_API_KEY 環境變數")
        print("請在 .env 文件中設置你的 Groq API key")
        return False
    
    try:
        client = Groq(api_key=api_key)
        
        # 簡單的測試請求
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "你是一個友善的助手。"},
                {"role": "user", "content": "請簡單回覆 'API 連接成功！'"}
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ API 連接成功！")
        print(f"📝 回應: {result}")
        return True
        
    except Exception as e:
        print(f"❌ API 連接失敗: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 測試 Groq API 連接...")
    test_groq_connection()
