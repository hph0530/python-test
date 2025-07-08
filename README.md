# YouTube 多格式下載器

一個簡單易用的 Python 應用程式，可以從 YouTube 下載影片為 MP4 格式或音訊為 MP3 格式。

## 功能特色

- 支援 YouTube 影片下載為 MP4 格式
- 支援 YouTube 音訊下載為 MP3 格式
- 自動選擇最佳品質
- 友善的命令列介面
- 錯誤處理和進度顯示

## 系統需求

- Python 3.7 或更高版本
- FFmpeg (用於音訊轉換)

## 安裝步驟

### 1. 安裝 Python
確保你的系統已安裝 Python 3.7 或更高版本。

### 2. 安裝 FFmpeg

**Windows:**
1. 從 [FFmpeg 官網](https://ffmpeg.org/download.html) 下載
2. 解壓縮到任意資料夾
3. 將 `bin` 資料夾路徑加入系統環境變數 PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 3. 設定專案環境

```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安裝依賴套件
pip install -r requirements.txt
```

## 快速開始

### 方法一：使用快速啟動腳本（推薦）

**Windows:**
```bash
# 雙擊 run.bat 檔案，或在命令提示字元中執行：
run.bat
```

**Linux/macOS:**
```bash
# 給予執行權限
chmod +x run.sh

# 執行程式
./run.sh
```

### 方法二：手動安裝和執行

```bash
# 1. 執行安裝腳本
python setup.py

# 2. 啟動虛擬環境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. 測試安裝
python test_downloader.py

# 4. 執行程式
python youtube_downloader.py
```

## 使用方法

程式啟動後會顯示選單：
1. **下載 MP4 影片** - 下載完整影片檔案
2. **下載 MP3 音訊** - 僅下載音訊並轉換為 MP3
3. **檢查 FFmpeg 狀態** - 確認 FFmpeg 是否正確安裝
4. **退出程式**

### 下載流程：
1. 選擇下載格式
2. 輸入 YouTube 影片網址
3. 確認影片資訊
4. 確認下載
5. 檔案會下載到 `downloads/` 資料夾

## 注意事項

- 請確保你有權限下載該影片
- 某些影片可能因地區限制無法下載
- 下載速度取決於你的網路連線
- 請遵守 YouTube 的服務條款

## 線上版本

你也可以使用線上版本，無需安裝任何軟體：
[YouTube 下載器線上版](https://your-app-name.streamlit.app) *(部署後會更新連結)*

## 部署到 Streamlit Cloud

### 步驟 1：準備 GitHub 倉庫
1. 在 GitHub 建立新的倉庫
2. 將專案檔案上傳到倉庫：
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/你的用戶名/你的倉庫名.git
   git push -u origin main
   ```

### 步驟 2：部署到 Streamlit Cloud
1. 前往 [Streamlit Cloud](https://streamlit.io/cloud)
2. 使用 GitHub 帳號登入
3. 點擊 "New app"
4. 選擇你的倉庫和 `web_ui.py` 檔案
5. 點擊 "Deploy!"

幾分鐘後，你的應用就會在網路上線！

## 授權

本專案僅供學習和研究使用。 