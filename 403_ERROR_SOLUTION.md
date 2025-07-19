# 🔧 解決 YouTube 403 Forbidden 錯誤

## 問題描述
當您嘗試下載 YouTube 影片時，可能會遇到以下錯誤：
```
ERROR: unable to download video data: HTTP Error 403: Forbidden
```

這是因為 YouTube 檢測到自動化下載行為並阻止了請求。

## 🛠️ 解決方案

### 方案 1：使用 Cookies（推薦）

#### 步驟 1：獲取 Cookies
1. **安裝瀏覽器擴充功能**：
   - **Chrome**: 安裝 "Get cookies.txt" 或 "EditThisCookie"
   - **Firefox**: 安裝 "cookies.txt"

2. **登入 YouTube**：
   - 前往 [YouTube](https://www.youtube.com)
   - 登入您的 Google 帳號

3. **匯出 Cookies**：
   - 點擊瀏覽器擴充功能圖示
   - 選擇 "Export" 或 "匯出"
   - 選擇 "cookies.txt" 格式
   - 下載 cookies.txt 檔案

#### 步驟 2：放置 Cookies 檔案
- 將 `cookies.txt` 檔案放在專案根目錄（與 `youtube_downloader.py` 同一層）
- 重新啟動應用程式

### 方案 2：更新 yt-dlp
```bash
pip install --upgrade yt-dlp
```

### 方案 3：使用代理伺服器
如果您在特定地區，可能需要使用代理伺服器：
```bash
pip install yt-dlp[websockets]
```

## 🧪 測試修復

### 方法 1：使用測試腳本
```bash
python cookies_setup.py
```

### 方法 2：手動測試
```bash
yt-dlp --cookies cookies.txt "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
```

## 📋 常見問題

### Q: 為什麼會出現 403 錯誤？
A: YouTube 實施了反爬蟲機制，當檢測到自動化下載時會阻止請求。

### Q: Cookies 檔案安全嗎？
A: Cookies 檔案包含您的登入資訊，請妥善保管，不要分享給他人。

### Q: 如果還是無法下載怎麼辦？
A: 嘗試以下方法：
1. 更新 yt-dlp 到最新版本
2. 使用不同的網路連線
3. 等待一段時間後再試
4. 嘗試下載其他影片

### Q: 可以批量下載嗎？
A: 可以，但建議：
1. 在下載之間添加延遲
2. 不要同時下載太多檔案
3. 使用 cookies 檔案

## 🔄 自動重試機制

程式已經內建了重試機制：
- 最多重試 3 次
- 每次重試之間有隨機延遲
- 使用不同的 User-Agent

## 📞 需要幫助？

如果以上方法都無法解決問題，請：
1. 檢查網路連線
2. 確認影片是否可公開存取
3. 嘗試使用不同的 YouTube 影片
4. 聯繫技術支援

## 🎯 最佳實踐

1. **定期更新 yt-dlp**：
   ```bash
   pip install --upgrade yt-dlp
   ```

2. **使用 cookies 檔案**：
   - 定期更新 cookies 檔案
   - 確保 YouTube 帳號已登入

3. **合理使用**：
   - 不要過度頻繁地下載
   - 遵守 YouTube 的服務條款
   - 僅下載您有權限的內容

4. **備用方案**：
   - 準備多個 cookies 檔案
   - 使用不同的網路連線
   - 考慮使用 VPN

---

**注意**：本工具僅供學習和研究使用，請遵守相關法律法規和服務條款。 