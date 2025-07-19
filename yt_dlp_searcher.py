from yt_dlp import YoutubeDL
import re

class YtDlpSearcher:
    """用 yt-dlp 搜尋 YouTube 影片，不需 API 金鑰"""
    
    def __init__(self, max_results=5):
        self.max_results = max_results

    def search(self, query, max_results=None):
        """
        搜尋 YouTube 影片
        
        Args:
            query (str): 搜尋關鍵字
            max_results (int): 最大結果數量
            
        Returns:
            list: 搜尋結果列表
        """
        if max_results is None:
            max_results = self.max_results
            
        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'skip_download': True,
                'no_warnings': True,
                'ignoreerrors': True,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                search_url = f"ytsearch{max_results}:{query}"
                result = ydl.extract_info(search_url, download=False)
                
                if not result or 'entries' not in result:
                    print(f"搜尋失敗: 無法取得結果")
                    return []
                
                entries = result.get('entries', [])
                processed = []
                
                for video in entries:
                    if not video:
                        continue
                        
                    # 處理時長格式
                    duration = video.get('duration', 0)
                    if duration:
                        duration_str = self._format_duration(duration)
                    else:
                        duration_str = "未知"
                    
                    # 處理縮圖
                    thumbnails = video.get('thumbnails', [])
                    thumbnail_url = ""
                    if thumbnails:
                        # 選擇中等品質的縮圖
                        for thumb in thumbnails:
                            if thumb.get('width', 0) >= 120:
                                thumbnail_url = thumb.get('url', '')
                                break
                        if not thumbnail_url and thumbnails:
                            thumbnail_url = thumbnails[0].get('url', '')
                    
                    processed_video = {
                        'title': video.get('title', '無標題'),
                        'url': f"https://www.youtube.com/watch?v={video.get('id', '')}",
                        'thumbnail': thumbnail_url,
                        'duration': duration_str,
                        'view_count': video.get('view_count', 0),
                        'uploader': video.get('uploader', '未知上傳者'),
                        'upload_date': self._format_date(video.get('upload_date', '')),
                        'description': video.get('description', '')[:200] + '...' if video.get('description', '') else '',
                        'video_id': video.get('id', '')
                    }
                    processed.append(processed_video)
                
                print(f"成功搜尋到 {len(processed)} 個影片")
                return processed
                
        except Exception as e:
            print(f"搜尋時發生錯誤: {e}")
            return []
    
    def _format_duration(self, seconds):
        """格式化時長"""
        if not seconds:
            return "未知"
        
        try:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes}:{remaining_seconds:02d}"
        except:
            return "未知"
    
    def _format_date(self, date_str):
        """格式化日期"""
        if not date_str or len(date_str) != 8:
            return "未知"
        
        try:
            year = date_str[:4]
            month = date_str[4:6]
            day = date_str[6:8]
            return f"{year}-{month}-{day}"
        except:
            return "未知" 