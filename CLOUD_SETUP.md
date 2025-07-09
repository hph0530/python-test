# 雲端硬碟設定說明

本專案支援自動上傳下載的檔案到多種雲端硬碟服務。請依照以下說明進行設定。

## 目錄結構

```
cloud_config/
├── google_credentials.json    # Google Drive 認證檔案
├── google_token.json         # Google Drive 存取權杖（自動生成）
├── dropbox_token.txt         # Dropbox 存取權杖
└── onedrive_config.json      # OneDrive 設定檔案
```

## Google Drive 設定

### 1. 建立 Google Cloud 專案
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Drive API

### 2. 建立 OAuth 2.0 憑證
1. 在 Google Cloud Console 中，前往「API 和服務」>「憑證」
2. 點擊「建立憑證」>「OAuth 2.0 用戶端 ID」
3. 選擇應用程式類型為「桌面應用程式」
4. 下載 JSON 憑證檔案

### 3. 設定認證檔案
1. 建立 `cloud_config` 目錄（如果不存在）
2. 將下載的 JSON 檔案重新命名為 `google_credentials.json`
3. 將檔案放在 `cloud_config` 目錄中

### 4. 首次使用
首次使用時，程式會開啟瀏覽器要求您授權存取 Google Drive。授權後，存取權杖會自動儲存在 `google_token.json` 中。

## Dropbox 設定

### 1. 建立 Dropbox 應用程式
1. 前往 [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. 點擊「建立應用程式」
3. 選擇「Dropbox API」
4. 選擇「完整 Dropbox」存取權限
5. 為應用程式命名

### 2. 生成 Access Token
1. 在應用程式設定頁面，前往「OAuth 2」標籤
2. 在「Generated access token」區段，點擊「Generate」
3. 複製生成的 access token

### 3. 設定 Token 檔案
1. 建立 `cloud_config/dropbox_token.txt` 檔案
2. 將 access token 貼入檔案中（不要包含引號或額外空格）

## OneDrive 設定

### 1. 註冊 Azure 應用程式
1. 前往 [Azure Portal](https://portal.azure.com/)
2. 前往「Azure Active Directory」>「應用程式註冊」
3. 點擊「新增註冊」
4. 為應用程式命名並選擇支援的帳戶類型

### 2. 設定 API 權限
1. 在應用程式頁面，前往「API 權限」
2. 點擊「新增權限」
3. 選擇「Microsoft Graph」
4. 選擇「應用程式權限」
5. 搜尋並選擇以下權限：
   - `Files.ReadWrite.All`
   - `Sites.ReadWrite.All`
6. 點擊「授與管理員同意」

### 3. 建立用戶端密碼
1. 前往「憑證和密碼」
2. 點擊「新增用戶端密碼」
3. 設定描述和到期時間
4. 複製生成的密碼值

### 4. 設定設定檔案
建立 `cloud_config/onedrive_config.json` 檔案，內容如下：

```json
{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "tenant_id": "your_tenant_id"
}
```

- `client_id`: 應用程式註冊頁面中的「應用程式 (用戶端) ID」
- `client_secret`: 剛才建立的用戶端密碼值
- `tenant_id`: 目錄 (租用戶) ID

## 使用方式

1. 安裝必要的 Python 套件：
   ```bash
   pip install -r requirements.txt
   ```

2. 依照上述說明設定您想要使用的雲端服務

3. 執行程式：
   ```bash
   streamlit run web_ui.py
   ```

4. 在網頁介面中：
   - 勾選「啟用自動上傳到雲端硬碟」
   - 選擇要使用的雲端服務
   - 下載影片時會自動上傳到選定的雲端硬碟

## 注意事項

- 請妥善保管您的認證檔案和權杖，不要分享給他人
- Google Drive 的存取權杖會自動更新，無需手動管理
- Dropbox 的 access token 不會過期，但可以隨時在 App Console 中重新生成
- OneDrive 的用戶端密碼有到期時間，請注意更新
- 上傳的檔案會自動建立分享連結，方便存取

## 故障排除

### Google Drive 問題
- 確保 `google_credentials.json` 檔案格式正確
- 檢查 Google Drive API 是否已啟用
- 確認應用程式有適當的權限

### Dropbox 問題
- 確認 access token 正確且未過期
- 檢查應用程式權限設定
- 確認檔案路徑格式正確

### OneDrive 問題
- 確認所有設定值正確
- 檢查 API 權限是否已授與
- 確認用戶端密碼未過期

### 一般問題
- 檢查網路連線
- 確認雲端服務帳戶有足夠的儲存空間
- 查看程式日誌以獲取詳細錯誤訊息 