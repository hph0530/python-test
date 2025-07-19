# 🚀 GitHub 部署指南

本指南將幫助您將 YouTube 下載器與音樂播放器部署到 GitHub，並設定私有存取，讓只有有連結的人可以使用。

## 📋 部署步驟

### 步驟 1: 準備 GitHub 倉庫

1. **登入 GitHub**
   - 前往 [GitHub.com](https://github.com)
   - 使用您的 GitHub 帳號登入

2. **創建新的私有倉庫**
   - 點擊右上角的 "+" 按鈕
   - 選擇 "New repository"
   - 填寫倉庫資訊：
     - **Repository name**: `youtube-downloader-music-player`
     - **Description**: `YouTube 下載器與音樂播放器 - 家庭專用`
     - **Visibility**: 選擇 **Private** (私有)
     - **不要**勾選 "Add a README file"
   - 點擊 "Create repository"

### 步驟 2: 上傳程式碼到 GitHub

在您的專案目錄中執行以下命令：

```bash
# 初始化 Git 倉庫
git init

# 添加所有檔案
git add .

# 提交變更
git commit -m "Initial commit: YouTube 下載器與音樂播放器"

# 添加遠端倉庫
git remote add origin https://github.com/您的用戶名/youtube-downloader-music-player.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 步驟 3: 設定 Streamlit Cloud

1. **前往 Streamlit Cloud**
   - 前往 [share.streamlit.io](https://share.streamlit.io)
   - 使用 GitHub 帳號登入

2. **部署應用程式**
   - 點擊 "New app"
   - 選擇您的倉庫：`youtube-downloader-music-player`
   - 選擇主檔案：`integrated_web_player.py`
   - 點擊 "Deploy!"

### 步驟 4: 設定私有存取

1. **在 Streamlit Cloud 中設定**
   - 部署完成後，點擊應用程式設定
   - 在 "Access" 部分，選擇 "Private"
   - 這樣只有有連結的人才能存取

2. **分享連結**
   - 複製應用程式的 URL
   - 將連結分享給您的家人

## 🔧 重要設定

### 1. 確保敏感檔案不被上傳

檢查 `.gitignore` 檔案是否包含：

```
# 雲端設定
cloud_config/
*.json

# 虛擬環境
venv/
env/

# Python 快取
__pycache__/
*.pyc

# 下載檔案
downloads/
*.mp3
*.mp4

# 系統檔案
.DS_Store
Thumbs.db
```

### 2. 設定雲端服務 (可選)

如果您想要使用雲端上傳功能：

1. **Google Drive 設定**
   - 前往 [Google Cloud Console](https://console.cloud.google.com)
   - 創建新專案
   - 啟用 Google Drive API
   - 創建服務帳號並下載 JSON 憑證

2. **在 Streamlit Cloud 中設定 Secrets**
   - 在 Streamlit Cloud 應用程式設定中
   - 前往 "Secrets" 標籤
   - 添加您的雲端服務憑證

## 📱 使用方式

### 給家人的使用說明

1. **開啟應用程式**
   - 點擊您分享的連結
   - 等待應用程式載入

2. **下載 YouTube 影片**
   - 在「直接下載」標籤頁輸入 YouTube 網址
   - 選擇 MP4 或 MP3 格式
   - 點擊下載

3. **播放音樂**
   - 在「音樂播放器」標籤頁
   - 掃描音樂資料夾
   - 選擇要播放的音樂

4. **搜尋影片**
   - 在「搜尋下載」標籤頁
   - 輸入關鍵字搜尋
   - 選擇要下載的影片

## 🔒 安全性考量

### 1. 私有倉庫
- 確保 GitHub 倉庫設為私有
- 只有您邀請的人才能看到程式碼

### 2. 應用程式存取
- Streamlit Cloud 應用程式設為私有
- 只有有連結的人才能使用

### 3. 雲端服務
- 使用服務帳號而非個人帳號
- 定期更新 API 金鑰

## 🛠️ 故障排除

### 常見問題

1. **部署失敗**
   - 檢查 `requirements.txt` 是否包含所有依賴
   - 確保主檔案名稱正確

2. **雲端上傳不工作**
   - 檢查 Streamlit Cloud 中的 Secrets 設定
   - 確認 API 金鑰有效

3. **音訊播放問題**
   - 確保瀏覽器允許音訊播放
   - 檢查系統音訊設定

### 更新應用程式

當您修改程式碼後：

```bash
# 提交變更
git add .
git commit -m "更新功能"
git push

# Streamlit Cloud 會自動重新部署
```

## 📞 支援

如果遇到問題：

1. 檢查 Streamlit Cloud 的部署日誌
2. 確認所有依賴都已安裝
3. 測試本地版本是否正常運作

## 🎉 完成！

部署完成後，您的家人就可以通過分享的連結使用您的 YouTube 下載器與音樂播放器了！

---

**注意**: 請確保遵守 YouTube 的服務條款，僅下載您有權限的內容。 