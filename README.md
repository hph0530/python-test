# YouTube 多格式下載器 & 音樂播放器

一個功能強大的 Python 應用程式，可以從 YouTube 下載影片為 MP4 格式或音訊為 MP3 格式，並支援自動上傳到雲端硬碟，同時內建音樂播放器功能。

## 功能特色

- 支援 YouTube 影片下載為 MP4 格式
- 支援 YouTube 音訊下載為 MP3 格式
- 自動選擇最佳品質
- 友善的網頁介面 (Streamlit)
- 錯誤處理和進度顯示
- **🆕 YouTube 搜尋功能**
  - 使用 yt-dlp 內建搜尋，穩定可靠
  - 顯示前五個搜尋結果
  - 支援批量選擇和下載
  - 支援中英文關鍵字搜尋
- **🆕 自動上傳到雲端硬碟**
  - Google Drive
  - Dropbox
  - OneDrive
- 支援多服務同時上傳
- 自動建立分享連結
- **🎵 內建音樂播放器**
  - 支援多種音訊格式 (MP3, WAV, OGG, FLAC, M4A)
  - 播放控制 (播放、暫停、停止、上一首、下一首)
  - 音量控制
  - 隨機播放和重複播放
  - 播放清單管理
  - **📱 iPhone 背景播放支援**
  - 支援背景播放
  - 控制中心整合
  - 鎖定螢幕控制
  - AirPods 支援

## 系統需求

- Python 3.7 或更高版本
- FFmpeg (用於音訊轉換)
- pygame (用於音樂播放)
- mutagen (用於音訊檔案資訊讀取)

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
python test_music_player.py

# 4. 執行程式
python youtube_downloader.py
```

## 使用方法

### 整合介面 (推薦)

1. 執行程式：
   ```bash
   streamlit run integrated_ui.py
   ```

2. 在瀏覽器中開啟顯示的網址

3. 使用方式：

#### 🔗 直接下載標籤頁
   - 輸入 YouTube 影片網址
   - 選擇下載格式 (MP4 或 MP3)
   - 選擇是否啟用雲端上傳
   - 點擊下載按鈕
   - **下載 MP3 後可立即在播放器中播放**

#### 🔍 搜尋下載標籤頁
   - 輸入搜尋關鍵字（支援中英文）
   - 點擊搜尋按鈕
   - 查看前五個搜尋結果
   - 勾選要下載的影片
   - 選擇下載格式和雲端上傳設定
   - 點擊批量下載按鈕

#### 🎵 音樂播放器標籤頁
   - 初始化播放器
   - 掃描音樂資料夾
   - 使用播放控制按鈕
   - 調整音量和播放模式
   - 瀏覽播放清單
   - 點擊歌曲直接播放

#### 📱 iPhone 背景播放標籤頁
   - 了解背景播放功能
   - 查看使用說明
   - 啟用/停用背景播放

### 獨立音樂播放器介面

如果您只需要音樂播放功能：
```bash
streamlit run music_player_ui.py
```

### 雲端硬碟設定

如需使用自動上傳功能，請先設定雲端服務：

1. 查看詳細設定說明：`CLOUD_SETUP.md`
2. 建立 `cloud_config` 目錄
3. 依照說明設定您想要使用的雲端服務
4. 測試設定：`python test_cloud_upload.py`

## 音樂播放器功能詳解

### 🎮 播放控制
- **播放/暫停**: 控制音樂播放狀態
- **停止**: 完全停止播放
- **上一首/下一首**: 切換歌曲
- **音量控制**: 調整播放音量
- **播放模式**: 隨機播放和重複播放

### 📋 播放清單管理
- **自動掃描**: 自動掃描 downloads 資料夾中的音樂檔案
- **歌曲資訊**: 顯示標題、藝術家、專輯、時長等資訊
- **播放進度**: 實時顯示播放進度
- **批量操作**: 播放全部、重新整理清單

### 📱 iPhone 背景播放
- **背景播放**: 即使關閉應用程式，音樂仍會繼續播放
- **控制中心整合**: 可以在 iPhone 控制中心控制播放
- **鎖定螢幕控制**: 在鎖定螢幕上顯示播放控制
- **AirPods 支援**: 完美支援 AirPods 和其他藍牙耳機

### 🎧 耳機控制
- **單擊**: 播放/暫停
- **雙擊**: 下一首
- **三擊**: 上一首
- **長按**: 語音助手（Siri）

## 支援的格式

### 下載格式
- **MP4**: 高品質影片格式
- **MP3**: 高品質音訊格式

### 播放格式
- **MP3**: 最常見的音訊格式
- **WAV**: 無損音訊格式
- **OGG**: 開放音訊格式
- **FLAC**: 無損壓縮格式
- **M4A**: Apple 音訊格式

## 測試功能

### 測試下載器
```bash
python test_downloader.py
```

### 測試音樂播放器
```bash
python test_music_player.py
```

### 測試雲端上傳
```bash
python test_cloud_upload.py
```

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
7. **如果是 MP3 格式，可以立即在音樂播放器中播放**

## 注意事項

- 請確保你有權限下載該影片
- 某些影片可能因地區限制無法下載
- 下載速度取決於你的網路連線
- 請遵守 YouTube 的服務條款
- 雲端上傳功能需要正確設定相關服務的 API 憑證
- 請妥善保管您的雲端服務認證檔案
- 搜尋功能使用 yt-dlp 內建搜尋，穩定可靠且無需 API 金鑰
- 音樂播放器需要 pygame 和 mutagen 套件
- iPhone 背景播放在實際設備上效果最佳

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
4. 選擇你的倉庫和 `integrated_ui.py` 檔案
5. 點擊 "Deploy!"

幾分鐘後，你的應用就會在網路上線！

## 授權

本專案僅供學習和研究使用。 