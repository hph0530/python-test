@echo off
echo 🚀 YouTube 下載器與音樂播放器部署腳本
echo ================================================

echo.
echo 📋 檢查必要檔案...
if not exist "integrated_web_player.py" (
    echo ❌ 錯誤: 找不到 integrated_web_player.py
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ❌ 錯誤: 找不到 requirements.txt
    pause
    exit /b 1
)

echo ✅ 必要檔案檢查完成

echo.
echo 🔧 初始化 Git 倉庫...
if not exist ".git" (
    git init
    echo ✅ Git 倉庫初始化完成
) else (
    echo ℹ️ Git 倉庫已存在
)

echo.
echo 📁 添加檔案到 Git...
git add .

echo.
echo 💾 提交變更...
git commit -m "更新: YouTube 下載器與音樂播放器"

echo.
echo 🌐 推送到 GitHub...
echo 請確保您已經在 GitHub 上創建了私有倉庫
echo 並設定了遠端倉庫連結
echo.
echo 如果還沒有設定遠端倉庫，請執行：
echo git remote add origin https://github.com/您的用戶名/youtube-downloader-music-player.git
echo.
echo 然後執行：
echo git push -u origin main
echo.

set /p choice="是否現在推送到 GitHub? (y/n): "
if /i "%choice%"=="y" (
    git push -u origin main
    echo.
    echo ✅ 推送完成！
    echo.
    echo 📝 下一步：
    echo 1. 前往 https://share.streamlit.io
    echo 2. 使用 GitHub 帳號登入
    echo 3. 點擊 "New app"
    echo 4. 選擇您的倉庫
    echo 5. 選擇主檔案: integrated_web_player.py
    echo 6. 點擊 "Deploy!"
    echo.
    echo 🔒 部署完成後，記得設定為私有存取
) else (
    echo.
    echo ℹ️ 您可以稍後手動推送
    echo 使用命令: git push -u origin main
)

echo.
echo 🎉 部署腳本執行完成！
pause 