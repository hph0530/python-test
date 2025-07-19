#!/usr/bin/env python3
"""
YouTube 搜尋功能演示腳本
展示如何使用新的搜尋和下載功能
"""

def demo_search_and_download():
    """演示搜尋和下載功能"""
    print("🎬 YouTube 搜尋功能演示")
    print("=" * 60)
    
    try:
        from youtube_searcher import YouTubeSearcher
        from youtube_downloader import YouTubeDownloader
        
        # 創建搜尋器
        searcher = YouTubeSearcher()
        
        # 演示搜尋
        search_query = input("請輸入要搜尋的關鍵字 (例如: Python 教學): ").strip()
        if not search_query:
            search_query = "Python 教學"
            print(f"使用預設關鍵字: {search_query}")
        
        print(f"\n🔍 正在搜尋: {search_query}")
        results = searcher.get_top_videos_by_views(search_query, max_results=3)
        
        if not results:
            print("❌ 沒有找到任何結果")
            return
        
        print(f"\n✅ 找到 {len(results)} 個結果:")
        print("-" * 60)
        
        # 顯示搜尋結果
        for i, video in enumerate(results, 1):
            print(f"\n📺 結果 {i}:")
            print(f"   標題: {video['title']}")
            print(f"   上傳者: {video['uploader']}")
            print(f"   觀看次數: {video['view_count']:,}")
            print(f"   時長: {video['duration']}")
            print(f"   URL: {video['url']}")
        
        # 詢問是否要下載
        print("\n" + "=" * 60)
        download_choice = input("是否要下載第一個結果？(y/n): ").strip().lower()
        
        if download_choice in ['y', 'yes', '是']:
            video = results[0]
            print(f"\n🚀 開始下載: {video['title']}")
            
            # 選擇格式
            format_choice = input("選擇格式 (1: MP4, 2: MP3): ").strip()
            if format_choice == "2":
                format_name = "MP3"
                download_func = "download_mp3"
            else:
                format_name = "MP4"
                download_func = "download_mp4"
            
            print(f"📥 下載格式: {format_name}")
            
            # 執行下載
            try:
                downloader = YouTubeDownloader()
                
                if format_name == "MP3":
                    result = downloader.download_mp3(video['url'])
                else:
                    result = downloader.download_mp4(video['url'])
                
                if result.get('file_path'):
                    print(f"✅ 下載成功: {result['file_path']}")
                else:
                    print(f"❌ 下載失敗: {result.get('error', '未知錯誤')}")
                    
            except Exception as e:
                print(f"❌ 下載時發生錯誤: {e}")
        
        print("\n🎉 演示完成！")
        
    except ImportError as e:
        print(f"❌ 匯入錯誤: {e}")
        print("請確保已安裝所有必要的套件:")
        print("pip install -r requirements.txt")
        print("python install_search_deps.py")
    except Exception as e:
        print(f"❌ 演示失敗: {e}")

def show_usage_tips():
    """顯示使用提示"""
    print("\n💡 使用提示:")
    print("1. 在網頁介面中，切換到 '🔍 搜尋下載' 標籤頁")
    print("2. 輸入搜尋關鍵字並點擊搜尋")
    print("3. 查看按觀看次數排序的結果")
    print("4. 勾選要下載的影片")
    print("5. 選擇下載格式和雲端上傳設定")
    print("6. 點擊批量下載按鈕")
    print("\n🚀 啟動網頁介面: streamlit run web_ui.py")

if __name__ == "__main__":
    demo_search_and_download()
    show_usage_tips() 