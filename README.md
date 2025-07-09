# YouTube 多格式下載器

一個功能強大的 Python 應用程式，可以從 YouTube 下載影片為 MP4 格式或音訊為 MP3 格式，並支援自動上傳到雲端硬碟。

## 功能特色

- 支援 YouTube 影片下載為 MP4 格式
- 支援 YouTube 音訊下載為 MP3 格式
- 自動選擇最佳品質
- 友善的網頁介面 (Streamlit)
- 錯誤處理和進度顯示
- **🆕 自動上傳到雲端硬碟**
  - Google Drive
  - Dropbox
  - OneDrive
- 支援多服務同時上傳
- 自動建立分享連結

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

### 網頁介面 (推薦)

1. 執行程式：
   ```bash
   streamlit run web_ui.py
   ```

2. 在瀏覽器中開啟顯示的網址

3. 使用步驟：
   - 輸入 YouTube 影片網址
   - 選擇下載格式 (MP4 或 MP3)
   - 選擇是否啟用雲端上傳
   - 選擇要使用的雲端服務
   - 點擊下載按鈕

### 雲端硬碟設定

如需使用自動上傳功能，請先設定雲端服務：

1. 查看詳細設定說明：`CLOUD_SETUP.md`
2. 建立 `cloud_config` 目錄
3. 依照說明設定您想要使用的雲端服務
4. 測試設定：`python test_cloud_upload.py`

## 具體操作方式

### 1. 確認 .gitignore 有 cloud_config/
請打開您的 `.gitignore`，確認有這一行：
```
cloud_config/
```
這樣 Git 會自動忽略這個資料夾。

---

### 2. 如果 cloud_config 已經被加入 Git 追蹤，請執行：

在命令列輸入：
```bash
git rm -r --cached cloud_config
```
這樣會把 cloud_config 從 Git 追蹤中移除（但本地檔案還在，不會刪掉您的檔案）。

---

### 3. 提交變更
```bash
git add .gitignore
git commit -m "remove sensitive cloud_config from repo"
git push
```

---

### 4. 確認 GitHub 上的倉庫**沒有 cloud_config 目錄**  
- 到 GitHub 頁面檢查，應該看不到 cloud_config 這個資料夾。

---

這樣就完成第二步驟，  
您的 Google 憑證就不會被上傳到 GitHub，  
後續可以安全地進行 Streamlit Cloud 的 secrets 設定！

---

如果有任何步驟遇到問題，請把錯誤訊息或畫面貼給我，我會一步步協助您！

### 命令列介面

程式也支援命令列使用：
```bash
python youtube_downloader.py
```

### 下載流程：
1. 選擇下載格式
2. 輸入 YouTube 影片網址
3. 確認影片資訊
4. 確認下載
5. 檔案會下載到 `downloads/` 資料夾
6. **如果啟用自動上傳，檔案會自動上傳到選定的雲端硬碟**

## 注意事項

- 請確保你有權限下載該影片
- 某些影片可能因地區限制無法下載
- 下載速度取決於你的網路連線
- 請遵守 YouTube 的服務條款
- 雲端上傳功能需要正確設定相關服務的 API 憑證
- 請妥善保管您的雲端服務認證檔案

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