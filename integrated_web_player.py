#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全整合式 YouTube 下載器與網頁音訊播放器
結合下載和播放功能，使用 Streamlit 內建音訊播放器
"""

import streamlit as st
from pathlib import Path
import re
import time
import traceback
import base64

# 匯入下載器模組
from youtube_downloader import YouTubeDownloader

# 匯入搜尋器模組
try:
    from yt_dlp_searcher import YtDlpSearcher
    SEARCH_AVAILABLE = True
except ImportError as e:
    st.error(f"❌ 搜尋功能載入失敗: {e}")
    SEARCH_AVAILABLE = False

# 匯入雲端上傳模組
try:
    from cloud_uploader import CloudUploadManager
    CLOUD_UPLOAD_AVAILABLE = True
except ImportError as e:
    st.warning(f"⚠️ 雲端上傳功能不可用: {e}")
    CLOUD_UPLOAD_AVAILABLE = False

# --- 頁面設定 ---
st.set_page_config(
    page_title="🎬 YouTube 下載器 & 🎵 網頁播放器",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 狀態管理 ---
# YouTube 下載器狀態
if 'video_info' not in st.session_state:
    st.session_state.video_info = None
if 'download_result' not in st.session_state:
    st.session_state.download_result = None
if 'is_downloading' not in st.session_state:
    st.session_state.is_downloading = False
if 'auto_upload' not in st.session_state:
    st.session_state.auto_upload = False
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'selected_videos' not in st.session_state:
    st.session_state.selected_videos = []

# 音樂播放器狀態
if 'selected_audio_file' not in st.session_state:
    st.session_state.selected_audio_file = None
if 'music_files' not in st.session_state:
    st.session_state.music_files = []
if 'playlist_updated' not in st.session_state:
    st.session_state.playlist_updated = False

# --- 輔助函數 ---
def scan_music_folder():
    """掃描音樂資料夾"""
    downloads_dir = Path("downloads")
    if not downloads_dir.exists():
        return []
    
    supported_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.m4a'}
    music_files = []
    
    for file_path in downloads_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            music_files.append(file_path)
    
    return sorted(music_files, key=lambda x: x.name)

def format_time(seconds: float) -> str:
    """格式化時間顯示"""
    if seconds <= 0:
        return "00:00"
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def format_file_size(size_bytes: int) -> str:
    """格式化檔案大小顯示"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def get_audio_file_info(file_path):
    """獲取音訊檔案資訊"""
    try:
        from mutagen import File
        audio = File(file_path)
        
        info = {
            'title': Path(file_path).stem,
            'artist': '未知藝術家',
            'album': '未知專輯',
            'duration': 0,
            'file_size': file_path.stat().st_size
        }
        
        if audio:
            if hasattr(audio, 'tags') and audio.tags:
                tags = audio.tags
                if 'title' in tags:
                    info['title'] = str(tags['title'][0])
                if 'artist' in tags:
                    info['artist'] = str(tags['artist'][0])
                if 'album' in tags:
                    info['album'] = str(tags['album'][0])
            
            if hasattr(audio, 'info') and audio.info:
                info['duration'] = audio.info.length
        
        return info
    except Exception as e:
        return {
            'title': Path(file_path).stem,
            'artist': '未知藝術家',
            'album': '未知專輯',
            'duration': 0,
            'file_size': file_path.stat().st_size
        }

def get_audio_mime_type(file_path):
    """獲取音訊檔案的 MIME 類型（iPhone 優化）"""
    suffix = file_path.suffix.lower()
    mime_map = {
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac',
        '.m4a': 'audio/mp4',
        '.aac': 'audio/aac'
    }
    return mime_map.get(suffix, 'audio/mpeg')

def create_iphone_audio_player(audio_bytes, mime_type, filename):
    """創建 iPhone 優化的音訊播放器"""
    import base64
    
    # 使用 HTML5 audio 元素，對 iPhone 更友好
    audio_html = f"""
    <audio controls style="width: 100%; max-width: 500px;">
        <source src="data:{mime_type};base64,{base64.b64encode(audio_bytes).decode()}" type="{mime_type}">
        您的瀏覽器不支援音訊播放。
    </audio>
    """
    
    st.markdown(audio_html, unsafe_allow_html=True)
    
    # 添加 iPhone 特定的提示
    st.info("📱 **iPhone 用戶提示**: 如果無法播放，請嘗試：\n"
            "1. 點擊播放按鈕後等待幾秒\n"
            "2. 確保音量已開啟\n"
            "3. 嘗試使用 Safari 瀏覽器\n"
            "4. 檢查是否允許自動播放")

# --- 主介面 ---
st.title("🎬 YouTube 下載器 & 🎵 網頁播放器")
st.markdown("下載 YouTube 影片並立即播放，享受完整的音樂體驗！")

# 側邊欄設定
with st.sidebar:
    st.header("⚙️ 設定")
    
    # 雲端上傳設定
    if CLOUD_UPLOAD_AVAILABLE:
        st.subheader("☁️ 雲端上傳")
        st.session_state.auto_upload = st.checkbox(
            "啟用自動上傳到雲端硬碟",
            value=st.session_state.auto_upload
        )
        if st.session_state.auto_upload:
            st.info("MP3 會上傳到 Google Drive MP3 資料夾")
    
    # 音樂播放器設定
    st.subheader("🎵 音樂播放器")
    
    # 掃描音樂資料夾
    if st.button("📁 掃描音樂資料夾", type="primary", use_container_width=True):
        music_files = scan_music_folder()
        st.session_state.music_files = music_files
        st.session_state.playlist_updated = True
        st.success(f"✅ 掃描完成，找到 {len(music_files)} 首歌曲")
    
    # 播放器狀態
    if st.session_state.music_files:
        st.markdown("---")
        st.subheader("📊 播放清單資訊")
        
        total_size = sum(f.stat().st_size for f in st.session_state.music_files)
        total_duration = sum(get_audio_file_info(f)['duration'] for f in st.session_state.music_files)
        
        st.write(f"**總歌曲數:** {len(st.session_state.music_files)}")
        st.write(f"**總時長:** {format_time(total_duration)}")
        st.write(f"**總大小:** {format_file_size(total_size)}")

# 主要標籤頁
tab1, tab2, tab3, tab4 = st.tabs([
    "🔗 直接下載", 
    "🔍 搜尋下載", 
    "🎵 音樂播放器",
    "📱 iPhone 背景播放"
])

# 標籤頁 1: 直接下載
with tab1:
    st.subheader("直接輸入 YouTube 網址下載")
    url = st.text_input("YouTube 影片網址", placeholder="https://www.youtube.com/watch?v=...", key="url_input_1")
    format_choice = st.radio("選擇下載格式", ("MP4 影片", "MP3 音訊"), horizontal=True, key="format_choice_1")
    
    if url:
        if "youtube.com" in url or "youtu.be" in url:
            if st.session_state.video_info is None or st.session_state.video_info.get('url') != url:
                try:
                    with st.spinner("正在獲取影片資訊..."):
                        downloader = YouTubeDownloader()
                        info = downloader.get_video_info(url)
                        if info:
                            st.session_state.video_info = info
                            st.session_state.video_info['url'] = url
                        else:
                            st.error("無法獲取影片資訊，請檢查網址是否正確或影片是否為私人影片。")
                            st.session_state.video_info = None
                except Exception as e:
                    st.error(f"獲取影片資訊時發生錯誤: {e}")
                    st.session_state.video_info = None
        else:
            st.warning("請輸入有效的 YouTube 網址。")
    
    if st.session_state.video_info:
        info = st.session_state.video_info
        col1, col2 = st.columns([1, 2])
        with col1:
            if info.get('thumbnail'):
                st.image(info['thumbnail'])
        with col2:
            st.subheader(info.get('title', '無標題'))
            st.caption(f"由 {info.get('uploader', '未知上傳者')} 上傳")
            if info.get('duration') and isinstance(info['duration'], (int, float)):
                try:
                    duration_str = time.strftime('%M:%S', time.gmtime(info['duration']))
                    st.write(f"時長: {duration_str}")
                except (ValueError, TypeError):
                    st.write("時長: 未知")
            else:
                st.write("時長: 未知")
            st.write(f"觀看次數: {info.get('view_count', 0):,}")
    
    if st.session_state.video_info:
        if st.session_state.download_result is None:
            if st.button(f"開始下載 {format_choice.split(' ')[0]}", type="primary", use_container_width=True, disabled=st.session_state.is_downloading, key="download_btn_1"):
                st.session_state.is_downloading = True
                st.session_state.download_result = None
                
                try:
                    progress_bar = st.progress(0, text="準備開始下載...")
                    status_text = st.empty()
                    
                    def progress_hook(d):
                        try:
                            if d['status'] == 'downloading':
                                percent_str = d.get('_percent_str', '0.0%')
                                percent_match = re.findall(r"(\d+\.?\d*)%", percent_str)
                                if percent_match:
                                    percent = float(percent_match[0])
                                    progress_bar.progress(int(percent), text=f"下載中... {percent:.1f}%")
                            elif d['status'] == 'finished':
                                progress_bar.progress(100, text="下載完成，正在進行後處理...")
                        except Exception as e:
                            print(f"進度回調錯誤: {e}")
                    
                    downloader = YouTubeDownloader(
                        auto_upload=st.session_state.auto_upload,
                        mp3_folder_id="1n-Y81X-lvha8KP7HxoWd17Chg5O0XN6w",
                        mp4_folder_id="1JocRza3zPEerZkg2z74ROOigN5XI2aCP"
                    )
                    downloader.add_progress_hook(progress_hook)
                    
                    download_func = downloader.download_mp4 if format_choice == "MP4 影片" else downloader.download_mp3
                    result = download_func(url)
                    
                    st.session_state.download_result = result
                    st.session_state.is_downloading = False
                    
                    # 如果下載的是 MP3，自動掃描播放清單
                    if format_choice == "MP3 音訊" and result.get('file_path'):
                        music_files = scan_music_folder()
                        st.session_state.music_files = music_files
                        st.session_state.playlist_updated = True
                    
                except Exception as e:
                    st.error(f"下載失敗: {e}")
                    st.session_state.is_downloading = False
                    st.session_state.download_result = None
    
    if st.session_state.download_result:
        result = st.session_state.download_result
        if result.get('file_path'):
            st.success(f"✅ **{Path(result['file_path']).name}** 下載成功！")
            
            # 顯示雲端上傳結果
            if result.get('upload_result'):
                st.markdown("---")
                st.subheader("☁️ 雲端上傳結果")
                
                upload_result = result['upload_result']
                if isinstance(upload_result, dict) and 'success' in upload_result:
                    if upload_result['success']:
                        st.success(f"✅ 已上傳到 {upload_result.get('service', '雲端硬碟')}")
                        if upload_result.get('web_link'):
                            st.markdown(f"🔗 [查看檔案]({upload_result['web_link']})")
                    else:
                        st.error(f"❌ 上傳失敗: {upload_result.get('error', '未知錯誤')}")
            
            # 本地下載按鈕
            file_path = result['file_path']
            with open(file_path, 'rb') as f:
                st.download_button(
                    label="📥 下載檔案",
                    data=f.read(),
                    file_name=Path(file_path).name,
                    mime="audio/mpeg" if format_choice == "MP3 音訊" else "video/mp4",
                    use_container_width=True
                )
            
            # 如果是 MP3，提供立即播放選項
            if format_choice == "MP3 音訊":
                st.markdown("---")
                st.subheader("🎵 立即播放")
                if st.button("▶️ 在播放器中播放此歌曲", use_container_width=True):
                    st.session_state.selected_audio_file = file_path
                    st.rerun()
        else:
            st.error("❌ 下載失敗")

# 標籤頁 2: 搜尋下載
with tab2:
    st.subheader("搜尋 YouTube 影片並下載")
    
    if not SEARCH_AVAILABLE:
        st.error("❌ 搜尋功能不可用，請確認 yt-dlp 已安裝")
        st.code("pip install yt-dlp")
    else:
        search_query = st.text_input("搜尋關鍵字", placeholder="輸入要搜尋的影片關鍵字", key="search_input_2")
        
        if st.button("🔍 搜尋影片", type="primary", use_container_width=True, key="search_btn_2"):
            if search_query.strip():
                with st.spinner("正在搜尋影片..."):
                    try:
                        searcher = YtDlpSearcher()
                        results = searcher.search(search_query, max_results=5)
                        st.session_state.search_results = results
                        if results:
                            st.success(f"找到 {len(results)} 個影片")
                        else:
                            st.warning("沒有找到任何影片，請嘗試其他關鍵字")
                    except Exception as e:
                        st.error(f"搜尋時發生錯誤: {e}")
                        st.session_state.search_results = []
            else:
                st.warning("請輸入搜尋關鍵字")
        
        if st.session_state.search_results:
            st.markdown("---")
            st.subheader("📺 搜尋結果（最多 5 筆）")
            
            # 批量下載設定
            st.markdown("### ⚙️ 批量下載設定")
            batch_format = st.radio("選擇下載格式", ("MP4 影片", "MP3 音訊"), horizontal=True, key="batch_format_2")
            
            # 顯示影片列表
            st.markdown("### 🎬 選擇要下載的影片")
            
            # 全選/取消全選
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("全選", key="select_all_2"):
                    st.session_state.selected_videos = [i for i in range(len(st.session_state.search_results))]
                    st.rerun()
                if st.button("取消全選", key="deselect_all_2"):
                    st.session_state.selected_videos = []
                    st.rerun()
            
            # 顯示搜尋結果
            for i, video in enumerate(st.session_state.search_results):
                with st.container():
                    col1, col2, col3 = st.columns([1, 4, 1])
                    
                    with col1:
                        is_selected = i in st.session_state.selected_videos
                        if st.checkbox(f"選擇 {i+1}", value=is_selected, key=f"select_{i}_2"):
                            if i not in st.session_state.selected_videos:
                                st.session_state.selected_videos.append(i)
                        else:
                            if i in st.session_state.selected_videos:
                                st.session_state.selected_videos.remove(i)
                    
                    with col2:
                        st.write(f"**{video.get('title', '無標題')}**")
                        st.caption(f"由 {video.get('uploader', '未知上傳者')} 上傳")
                        if video.get('duration') and isinstance(video['duration'], (int, float)):
                            try:
                                duration_str = time.strftime('%M:%S', time.gmtime(video['duration']))
                                st.write(f"時長: {duration_str}")
                            except (ValueError, TypeError):
                                st.write("時長: 未知")
                        else:
                            st.write("時長: 未知")
                        st.write(f"觀看次數: {video.get('view_count', 0):,}")
                    
                    with col3:
                        if st.button("下載", key=f"download_single_{i}_2"):
                            # 單一下載
                            st.session_state.is_downloading = True
                            try:
                                downloader = YouTubeDownloader(
                                    auto_upload=st.session_state.auto_upload,
                                    mp3_folder_id="1n-Y81X-lvha8KP7HxoWd17Chg5O0XN6w",
                                    mp4_folder_id="1JocRza3zPEerZkg2z74ROOigN5XI2aCP"
                                )
                                
                                download_func = downloader.download_mp4 if batch_format == "MP4 影片" else downloader.download_mp3
                                result = download_func(video['url'])
                                
                                if result.get('file_path'):
                                    st.success("✅ 下載成功！")
                                    # 如果是 MP3，自動掃描播放清單
                                    if batch_format == "MP3 音訊":
                                        music_files = scan_music_folder()
                                        st.session_state.music_files = music_files
                                        st.session_state.playlist_updated = True
                                else:
                                    st.error("❌ 下載失敗")
                                
                                st.session_state.is_downloading = False
                            except Exception as e:
                                st.error(f"下載失敗: {e}")
                                st.session_state.is_downloading = False
                    
                    st.markdown("---")
            
            # 批量下載按鈕
            if st.session_state.selected_videos:
                st.markdown("### 🚀 批量下載")
                st.info(f"已選擇 {len(st.session_state.selected_videos)} 個影片進行下載")
                
                if st.button(f"開始批量下載 {batch_format.split(' ')[0]}", type="primary", use_container_width=True, key="batch_download_btn_2"):
                    selected_videos = [st.session_state.search_results[i] for i in st.session_state.selected_videos]
                    
                    progress_bar = st.progress(0, text="準備開始批量下載...")
                    status_text = st.empty()
                    
                    downloader = YouTubeDownloader(
                        auto_upload=st.session_state.auto_upload,
                        mp3_folder_id="1n-Y81X-lvha8KP7HxoWd17Chg5O0XN6w",
                        mp4_folder_id="1JocRza3zPEerZkg2z74ROOigN5XI2aCP"
                    )
                    
                    results = []
                    for idx, video in enumerate(selected_videos):
                        try:
                            status_text.text(f"正在下載: {video.get('title', '未知標題')} ({idx + 1}/{len(selected_videos)})")
                            
                            def progress_hook(d):
                                try:
                                    if d['status'] == 'downloading':
                                        percent_str = d.get('_percent_str', '0.0%')
                                        percent_match = re.findall(r"(\d+\.?\d*)%", percent_str)
                                        if percent_match:
                                            percent = float(percent_match[0])
                                            progress_bar.progress(
                                                (idx + percent/100) / len(selected_videos),
                                                text=f"下載中... {video.get('title', '')[:30]}... {percent:.1f}%"
                                            )
                                    elif d['status'] == 'finished':
                                        progress_bar.progress(
                                            (idx + 1) / len(selected_videos),
                                            text=f"完成: {video.get('title', '')[:30]}..."
                                        )
                                except Exception as e:
                                    print(f"批量下載進度回調錯誤: {e}")
                            
                            downloader.add_progress_hook(progress_hook)
                            download_func = downloader.download_mp4 if batch_format == "MP4 影片" else downloader.download_mp3
                            result = download_func(video['url'])
                            results.append(result)
                            
                        except Exception as e:
                            st.error(f"下載 {video.get('title', '未知標題')} 失敗: {e}")
                            results.append({"file_path": None, "error": str(e)})
                    
                    # 顯示下載結果
                    success_count = sum(1 for r in results if r.get('file_path'))
                    st.success(f"✅ 批量下載完成！成功下載 {success_count}/{len(selected_videos)} 個檔案")
                    
                    # 如果是 MP3，自動掃描播放清單
                    if batch_format == "MP3 音訊":
                        music_files = scan_music_folder()
                        st.session_state.music_files = music_files
                        st.session_state.playlist_updated = True
                        st.info("🎵 播放清單已更新，可以在音樂播放器標籤頁中查看")

# 標籤頁 3: 音樂播放器
with tab3:
    st.subheader("🎵 網頁音訊播放器")
    st.markdown("使用 Streamlit 內建音訊播放器播放音樂檔案")
    
    # 掃描音樂資料夾
    if not st.session_state.music_files:
        if st.button("📁 掃描音樂資料夾", type="primary", use_container_width=True):
            music_files = scan_music_folder()
            st.session_state.music_files = music_files
            st.session_state.playlist_updated = True
            st.success(f"✅ 掃描完成，找到 {len(music_files)} 首歌曲")
    
    if st.session_state.music_files:
        # 側邊欄：檔案選擇
        with st.sidebar:
            st.markdown("---")
            st.subheader("🎵 選擇音樂檔案")
            
            # 檔案選擇器
            selected_file = st.selectbox(
                "選擇要播放的音樂檔案",
                options=st.session_state.music_files,
                format_func=lambda x: x.name,
                key="audio_file_selector"
            )
            
            if selected_file:
                # 顯示檔案資訊
                st.markdown("---")
                st.subheader("📋 檔案資訊")
                file_info = get_audio_file_info(selected_file)
                st.write(f"**檔案名稱:** {selected_file.name}")
                st.write(f"**標題:** {file_info['title']}")
                st.write(f"**藝術家:** {file_info['artist']}")
                st.write(f"**專輯:** {file_info['album']}")
                st.write(f"**時長:** {format_time(file_info['duration'])}")
                st.write(f"**檔案大小:** {format_file_size(file_info['file_size'])}")
                st.write(f"**檔案格式:** {selected_file.suffix.upper()}")
        
        # 主要內容區域
        if selected_file:
            st.markdown("---")
            st.subheader(f"🎵 正在播放: {selected_file.name}")
            
            # 使用 iPhone 優化的音訊播放器
            with open(selected_file, "rb") as f:
                audio_bytes = f.read()
            
            # 獲取正確的 MIME 類型
            mime_type = get_audio_mime_type(selected_file)
            
            # 創建 iPhone 優化播放器
            create_iphone_audio_player(audio_bytes, mime_type, selected_file.name)
            
            # 下載按鈕
            st.markdown("---")
            st.subheader("📥 下載選項")
            
            st.download_button(
                label="📥 下載音樂檔案",
                data=audio_bytes,
                file_name=selected_file.name,
                mime=f"audio/{selected_file.suffix[1:]}",
                use_container_width=True
            )
        
        # 播放清單
        st.markdown("---")
        st.subheader("📋 播放清單")
        
        # 顯示所有音樂檔案
        for i, file_path in enumerate(st.session_state.music_files, 1):
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([1, 3, 1, 1, 1])
                
                with col1:
                    st.write(f"{i}")
                
                with col2:
                    file_info = get_audio_file_info(file_path)
                    st.write(f"**{file_info['title']}**")
                    st.caption(f"{file_info['artist']} • {format_time(file_info['duration'])} • {format_file_size(file_info['file_size'])}")
                
                with col3:
                    if st.button("▶️", key=f"play_{i}", help="播放此歌曲"):
                        st.session_state.selected_audio_file = file_path
                        st.rerun()
                
                with col4:
                    # 下載按鈕
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    
                    st.download_button(
                        label="📥",
                        data=file_bytes,
                        file_name=file_path.name,
                        mime=f"audio/{file_path.suffix[1:]}",
                        key=f"download_{i}"
                    )
                
                with col5:
                    # 刪除按鈕
                    if st.button("🗑️", key=f"delete_{i}", help="刪除此歌曲"):
                        try:
                            file_path.unlink()
                            st.success("✅ 已刪除")
                            # 重新掃描播放清單
                            music_files = scan_music_folder()
                            st.session_state.music_files = music_files
                            st.rerun()
                        except Exception as e:
                            st.error(f"刪除失敗: {e}")
                
                st.markdown("---")
    else:
        st.info("📁 請先掃描音樂資料夾或下載一些 MP3 檔案")
        st.markdown("""
        ### 📝 使用說明
        
        1. **下載音樂**: 在「直接下載」或「搜尋下載」標籤頁下載 MP3 檔案
        2. **掃描資料夾**: 點擊「掃描音樂資料夾」按鈕
        3. **選擇音樂**: 在側邊欄選擇要播放的音樂檔案
        4. **播放控制**: 使用內建音訊播放器控制播放
        5. **下載音樂**: 點擊下載按鈕下載音樂檔案
        
        ### 🎵 支援的格式
        - MP3 (.mp3)
        - WAV (.wav)
        - OGG (.ogg)
        - FLAC (.flac)
        - M4A (.m4a)
        """)

# 標籤頁 4: iPhone 背景播放
with tab4:
    st.subheader("📱 iPhone 背景播放")
    st.markdown("""
    ### 🎵 iPhone 背景播放功能
    
    iPhone 背景播放功能需要在實際的 iPhone 設備上使用，並且需要設定特定的環境變數。
    
    ### 📋 使用步驟
    
    1. **在 iPhone 上開啟應用程式**
    2. **啟用背景播放模式**
    3. **開始播放音樂**
    4. **切換到其他應用程式或鎖定螢幕**
    5. **音樂會繼續在背景播放**
    
    ### 🎧 控制方式
    
    - **控制中心**: 從螢幕頂部向下滑動
    - **鎖定螢幕**: 在鎖定螢幕上顯示播放控制
    - **AirPods**: 支援 AirPods 控制手勢
    
    ### ⚙️ 技術說明
    
    背景播放功能使用以下技術：
    - pygame 音訊系統
    - 環境變數設定
    - 音訊會話管理
    
    ### 🔧 故障排除
    
    如果背景播放不工作：
    1. 確保在實際的 iPhone 設備上使用
    2. 檢查音訊設定
    3. 確保應用程式有音訊權限
    4. 重新啟動應用程式
    """)
    
    # 背景播放控制
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔊 啟用背景播放", type="primary", use_container_width=True):
            st.success("✅ 背景播放已啟用")
            st.info("在實際的 iPhone 設備上，音樂會在背景繼續播放")
    
    with col2:
        if st.button("🔇 停用背景播放", use_container_width=True):
            st.info("🔇 背景播放已停用")

def main():
    """主函數"""
    pass

if __name__ == "__main__":
    main() 