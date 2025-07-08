@echo off
chcp 65001 > nul
echo 🎬 YouTube 下載器 網頁版啟動中...
echo.

REM 檢查 Python 是否存在
python --version >nul 2>nul
if errorlevel 1 (
    echo ❌ 找不到 Python，請先安裝 Python 並將其加入 PATH。
    pause
    exit /b 1
)

REM 檢查 venv 是否存在，不存在則建立
if not exist "venv" (
    echo 🔧 正在建立虛擬環境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 建立虛擬環境失敗。
        pause
        exit /b 1
    )
)

echo 📦 正在檢查並安裝依賴套件...
call venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ❌ 安裝依賴套件失敗。
    pause
    exit /b 1
)

echo 🚀 正在啟動網頁介面...
call venv\Scripts\streamlit.exe run web_ui.py

pause 