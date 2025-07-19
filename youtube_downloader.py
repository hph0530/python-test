#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 多格式下載器
支援下載 YouTube 影片為 MP4 格式或音訊為 MP3 格式
並自動上傳到雲端硬碟
"""

import yt_dlp
from pathlib import Path
import logging
from typing import Optional, Dict, Any
import time
import random

# 匯入雲端上傳模組
try:
    from cloud_uploader import CloudUploadManager
    CLOUD_UPLOAD_AVAILABLE = True
except ImportError:
    CLOUD_UPLOAD_AVAILABLE = False
    logging.warning("雲端上傳模組無法載入，將無法使用自動上傳功能")

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class YouTubeDownloader:
    """
    YouTube 下載器核心功能類別。
    提供獲取影片資訊、下載 MP4 和 MP3 的功能。
    """
    
    def __init__(self, download_dir="downloads", auto_upload=False, mp3_folder_id=None, mp4_folder_id=None):
        """
        初始化下載器。
        :param download_dir: 下載檔案的儲存目錄。
        :param auto_upload: 是否自動上傳到雲端硬碟。
        :param mp3_folder_id: Google Drive MP3 目標資料夾 ID。
        :param mp4_folder_id: Google Drive MP4 目標資料夾 ID。
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.progress_hooks = []
        self.auto_upload = auto_upload
        self.mp3_folder_id = mp3_folder_id
        self.mp4_folder_id = mp4_folder_id
        self.cloud_manager_mp3 = CloudUploadManager(folder_id=mp3_folder_id) if self.auto_upload and CLOUD_UPLOAD_AVAILABLE else None
        self.cloud_manager_mp4 = CloudUploadManager(folder_id=mp4_folder_id) if self.auto_upload and CLOUD_UPLOAD_AVAILABLE else None

    def add_progress_hook(self, hook):
        """添加進度回調鉤子"""
        self.progress_hooks.append(hook)
    
    def _get_ydl_opts_base(self):
        """獲取基礎的 yt-dlp 選項，包含反 403 錯誤的設定"""
        return {
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': self.progress_hooks,
            # 反 403 錯誤設定
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            # 重試設定
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            # 延遲設定
            'sleep_interval': 1,
            'max_sleep_interval': 5,
            # 其他設定
            'ignoreerrors': False,
            'no_check_certificate': True,
            'prefer_insecure': True,
        }
    
    def upload_to_cloud(self, file_path: str, file_type: str = "mp4") -> Dict[str, Any]:
        """
        上傳檔案到雲端硬碟
        :param file_path: 要上傳的檔案路徑
        :param file_type: "mp3" 或 "mp4"，決定上傳到哪個資料夾
        :return: 上傳結果字典
        """
        if file_type == "mp3":
            cloud_manager = self.cloud_manager_mp3
        else:
            cloud_manager = self.cloud_manager_mp4
        if not cloud_manager:
            return {"success": False, "error": "雲端上傳功能未啟用或不可用"}
        try:
            return cloud_manager.upload(file_path)
        except Exception as e:
            logging.error(f"雲端上傳失敗: {e}")
            return {"success": False, "error": str(e)}

    def get_video_info(self, url):
        """
        獲取影片資訊，不進行下載。
        :param url: YouTube 影片網址。
        :return: 包含影片資訊的字典，或在失敗時返回 None。
        """
        ydl_opts = self._get_ydl_opts_base()
        ydl_opts.update({
            'extract_flat': True,
        })
        
        # 重試機制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    return {
                        'title': info.get('title', '未知標題'),
                        'thumbnail': info.get('thumbnail', ''),
                        'duration': info.get('duration', 0),
                        'uploader': info.get('uploader', '未知上傳者'),
                        'view_count': info.get('view_count', 0),
                    }
            except Exception as e:
                logging.warning(f"獲取影片資訊失敗 (嘗試 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(2, 5))  # 隨機延遲
                else:
                    logging.error(f"獲取影片資訊最終失敗: {e}")
                    return None

    def _download(self, url, ydl_opts):
        """
        內部下載方法。
        :param url: YouTube 影片網址。
        :param ydl_opts: yt-dlp 的選項。
        :return: 下載成功時返回檔案路徑，失敗時返回 None。
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    # 確保我們能獲取到下載後的檔案路徑
                    if info and '_filename' in info:
                        return info['_filename']
                    # 如果是播放列表，_filename 可能不存在於頂層
                    elif info and 'entries' in info and info['entries']:
                        return info['entries'][0]['_filename']
                    else:
                        # 作為備案，從 outtmpl 推斷檔名
                        # 這部分比較複雜，暫時先假設成功時能拿到 _filename
                        logging.warning("無法直接從返回資訊中確定檔名")
                        return None
            except Exception as e:
                logging.warning(f"下載失敗 (嘗試 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(3, 8))  # 隨機延遲
                else:
                    logging.error(f"下載最終失敗: {e}")
                    raise e

    def download_mp4(self, url):
        """
        下載高品質的 MP4 影片。
        :param url: YouTube 影片網址。
        :return: 包含檔案路徑和上傳結果的字典。
        """
        logging.info(f"準備下載 MP4: {url}")
        ydl_opts = self._get_ydl_opts_base()
        ydl_opts.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
        })
        
        file_path = self._download(url, ydl_opts)
        result = {"file_path": file_path, "upload_result": None}
        
        # 如果下載成功且啟用自動上傳，則上傳到雲端
        if file_path and self.auto_upload:
            logging.info("開始上傳到雲端硬碟（MP4 資料夾）...")
            result["upload_result"] = self.upload_to_cloud(file_path, file_type="mp4")
        
        return result

    def download_mp3(self, url):
        """
        下載並轉換為 MP3 音訊。
        :param url: YouTube 影片網址。
        :return: 包含檔案路徑和上傳結果的字典。
        """
        logging.info(f"準備下載 MP3: {url}")
        # 建立一個唯一的檔名模板，避免後處理器找不到檔案
        output_template = self.download_dir / f"%(title)s_%(id)s.%(ext)s"
        
        ydl_opts = self._get_ydl_opts_base()
        ydl_opts.update({
            'format': 'bestaudio/best',
            'outtmpl': str(output_template),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                original_filepath = ydl.prepare_filename(info)
                # 後處理後，副檔名會改變
                final_filepath = Path(original_filepath).with_suffix('.mp3')
                if final_filepath.exists():
                    file_path = str(final_filepath)
                    result = {"file_path": file_path, "upload_result": None}
                    
                    # 如果啟用自動上傳，則上傳到雲端
                    if self.auto_upload:
                        logging.info("開始上傳到雲端硬碟（MP3 資料夾）...")
                        result["upload_result"] = self.upload_to_cloud(file_path, file_type="mp3")
                    
                    return result
                else:
                    logging.error(f"MP3 轉換後找不到檔案: {final_filepath}")
                    return {"file_path": None, "upload_result": None}
        except Exception as e:
            logging.error(f"MP3 下載失敗: {e}")
            raise e 