#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Cookies 設定工具
幫助解決 403 Forbidden 錯誤
"""

import yt_dlp
import os
from pathlib import Path

def setup_cookies():
    """設定 cookies 來避免 403 錯誤"""
    print("🍪 開始設定 YouTube Cookies...")
    print("這將幫助解決 403 Forbidden 錯誤")
    
    # 檢查是否存在 cookies 檔案
    cookies_file = Path("cookies.txt")
    
    if cookies_file.exists():
        print(f"✅ 找到現有的 cookies 檔案: {cookies_file}")
        return str(cookies_file)
    
    print("📝 沒有找到 cookies.txt 檔案")
    print("請按照以下步驟獲取 cookies：")
    print()
    print("1. 安裝瀏覽器擴充功能：")
    print("   - Chrome: 'Get cookies.txt' 或 'EditThisCookie'")
    print("   - Firefox: 'cookies.txt'")
    print()
    print("2. 前往 YouTube 並登入您的帳號")
    print("3. 使用擴充功能匯出 cookies 為 cookies.txt 格式")
    print("4. 將 cookies.txt 檔案放在此專案根目錄")
    print()
    print("或者，您可以使用以下命令手動下載：")
    print("yt-dlp --cookies cookies.txt [影片URL]")
    
    return None

def test_with_cookies(url, cookies_file=None):
    """使用 cookies 測試下載"""
    print(f"🧪 測試下載: {url}")
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        'retries': 10,
        'fragment_retries': 10,
        'skip_unavailable_fragments': True,
        'sleep_interval': 1,
        'max_sleep_interval': 5,
        'no_check_certificate': True,
        'prefer_insecure': True,
    }
    
    if cookies_file and Path(cookies_file).exists():
        ydl_opts['cookiefile'] = cookies_file
        print("🍪 使用 cookies 檔案")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"✅ 成功獲取影片資訊: {info.get('title', '未知標題')}")
            return True
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

if __name__ == "__main__":
    # 設定 cookies
    cookies_file = setup_cookies()
    
    # 測試 URL（請替換為實際的影片 URL）
    test_url = input("請輸入要測試的 YouTube 影片 URL: ").strip()
    
    if test_url:
        test_with_cookies(test_url, cookies_file)
    else:
        print("未提供測試 URL") 