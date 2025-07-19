#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修復後的下載器
"""

from youtube_downloader import YouTubeDownloader
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_download():
    """測試下載功能"""
    print("🧪 開始測試修復後的下載器...")
    
    # 測試用的 YouTube 影片 URL（蕭煌奇的慢冷）
    test_url = "https://www.youtube.com/watch?v=example"  # 請替換為實際的 URL
    
    # 創建下載器實例
    downloader = YouTubeDownloader(auto_upload=False)
    
    try:
        print("📋 獲取影片資訊...")
        info = downloader.get_video_info(test_url)
        
        if info:
            print(f"✅ 成功獲取影片資訊:")
            print(f"   標題: {info['title']}")
            print(f"   上傳者: {info['uploader']}")
            print(f"   時長: {info['duration']} 秒")
            print(f"   觀看次數: {info['view_count']}")
            
            # 測試下載 MP3
            print("\n🎵 測試下載 MP3...")
            result = downloader.download_mp3(test_url)
            
            if result.get('file_path'):
                print(f"✅ MP3 下載成功: {result['file_path']}")
            else:
                print("❌ MP3 下載失敗")
                
        else:
            print("❌ 無法獲取影片資訊")
            
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    test_download() 