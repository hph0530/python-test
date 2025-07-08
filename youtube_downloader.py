#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 多格式下載器
支援下載 YouTube 影片為 MP4 格式或音訊為 MP3 格式
"""

import yt_dlp
from pathlib import Path
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class YouTubeDownloader:
    """
    YouTube 下載器核心功能類別。
    提供獲取影片資訊、下載 MP4 和 MP3 的功能。
    """
    
    def __init__(self, download_dir="downloads"):
        """
        初始化下載器。
        :param download_dir: 下載檔案的儲存目錄。
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.progress_hooks = []

    def add_progress_hook(self, hook):
        """添加進度回調鉤子"""
        self.progress_hooks.append(hook)

    def get_video_info(self, url):
        """
        獲取影片資訊，不進行下載。
        :param url: YouTube 影片網址。
        :return: 包含影片資訊的字典，或在失敗時返回 None。
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
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
            logging.error(f"獲取影片資訊失敗: {e}")
            return None

    def _download(self, url, ydl_opts):
        """
        內部下載方法。
        :param url: YouTube 影片網址。
        :param ydl_opts: yt-dlp 的選項。
        :return: 下載成功時返回檔案路徑，失敗時返回 None。
        """
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
            logging.error(f"下載失敗: {e}")
            # 將異常向上拋出，讓呼叫者處理
            raise e

    def download_mp4(self, url):
        """
        下載高品質的 MP4 影片。
        :param url: YouTube 影片網址。
        :return: 檔案路徑或 None。
        """
        logging.info(f"準備下載 MP4: {url}")
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'progress_hooks': self.progress_hooks,
            'quiet': True,
            'no_warnings': True,
        }
        return self._download(url, ydl_opts)

    def download_mp3(self, url):
        """
        下載並轉換為 MP3 音訊。
        :param url: YouTube 影片網址。
        :return: 檔案路徑或 None。
        """
        logging.info(f"準備下載 MP3: {url}")
        # 建立一個唯一的檔名模板，避免後處理器找不到檔案
        output_template = self.download_dir / f"%(title)s_%(id)s.%(ext)s"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(output_template),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': self.progress_hooks,
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                original_filepath = ydl.prepare_filename(info)
                # 後處理後，副檔名會改變
                final_filepath = Path(original_filepath).with_suffix('.mp3')
                if final_filepath.exists():
                    return str(final_filepath)
                else:
                    logging.error(f"MP3 轉換後找不到檔案: {final_filepath}")
                    return None
        except Exception as e:
            logging.error(f"MP3 下載失敗: {e}")
            raise e 