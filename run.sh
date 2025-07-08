#!/bin/bash
echo "🎬 YouTube 下載器 網頁版啟動中..."
echo

# 檢查 Python3 是否存在
if ! command -v python3 &> /dev/null
then
    echo "❌ 找不到 Python3，請先安裝 Python3。"
    exit 1
fi

# 檢查 venv 是否存在，不存在則建立
if [ ! -d "venv" ]; then
    echo "🔧 正在建立虛擬環境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 建立虛擬環境失敗。"
        exit 1
    fi
fi

# 啟動虛擬環境並安裝依賴
echo "📦 正在檢查並安裝依賴套件..."
source venv/bin/activate
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "❌ 安裝依賴套件失敗。"
    exit 1
fi

# 啟動 Streamlit 網頁介面
echo "🚀 正在啟動網頁介面..."
streamlit run web_ui.py 