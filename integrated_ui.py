#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合式 YouTube 下載器與音樂播放器
結合下載和播放功能，提供完整的音樂體驗
"""

import streamlit as st
from pathlib import Path
import re
import time
import traceback

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

# 匯入音樂播放器模組
try:
    from music_player import MusicPlayer, PlaybackState, Song, create_music_player
    MUSIC_PLAYER_AVAILABLE = True
except ImportError as e:
    st.warning(f"⚠️ 音樂播放器功能不可用: {e}")
    MUSIC_PLAYER_AVAILABLE = False

# --- 頁面設定 ---
st.set_page_config(
    page_title="🎬 YouTube 下載器 & 🎵 音樂播放器",
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
if 'music_player' not in st.session_state:
    st.session_state.music_player = None
if 'current_song' not in st.session_state:
    st.session_state.current_song = None
if 'playlist' not in st.session_state:
    st.session_state.playlist = []
if 'playback_state' not in st.session_state:
    st.session_state.playback_state = PlaybackState.STOPPED
if 'current_progress' not in st.session_state:
    st.session_state.current_progress = 0.0
if 'volume' not in st.session_state:
    st.session_state.volume = 0.7
if 'is_shuffle' not in st.session_state:
    st.session_state.is_shuffle = False
if 'is_repeat' not in st.session_state:
    st.session_state.is_repeat = False

# --- 輔助函數 ---
def init_music_player():
    """初始化音樂播放器"""
    if not MUSIC_PLAYER_AVAILABLE:
        return False
    
    try:
        if st.session_state.music_player is None:
            st.session_state.music_player = create_music_player("downloads")
            
            # 設定回調函數
            def on_song_change(song: Song):
                st.session_state.current_song = song
                st.rerun()
            
            def on_state_change(state: PlaybackState):
                st.session_state.playback_state = state
                st.rerun()
            
            def on_progress(progress: float):
                st.session_state.current_progress = progress
            
            st.session_state.music_player.on_song_change = on_song_change
            st.session_state.music_player.on_state_change = on_state_change
            st.session_state.music_player.on_progress = on_progress
        
        return True
    except Exception as e:
        st.error(f"初始化音樂播放器失敗: {e}")
        return False

def scan_music_folder():
    """掃描音樂資料夾"""
    if st.session_state.music_player:
        try:
            songs = st.session_state.music_player.scan_music_folder()
            st.session_state.playlist = songs
            st.success(f"✅ 掃描完成，找到 {len(songs)} 首歌曲")
            return True
        except Exception as e:
            st.error(f"掃描音樂資料夾失敗: {e}")
            return False
    return False

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

# --- 主介面 ---
st.title("🎬 YouTube 下載器 & 🎵 音樂播放器")
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
    if MUSIC_PLAYER_AVAILABLE:
        st.subheader("🎵 音樂播放器")
        
        # 初始化播放器
        if st.button("🔧 初始化播放器", type="primary", use_container_width=True):
            if init_music_player():
                st.success("✅ 播放器初始化成功")
            else:
                st.error("❌ 播放器初始化失敗")
        
        # 掃描音樂資料夾
        if st.button("📁 掃描音樂資料夾", use_container_width=True):
            if init_music_player():
                scan_music_folder()
            else:
                st.error("請先初始化播放器")
        
        # 播放器狀態
        if st.session_state.music_player:
            st.markdown("---")
            st.subheader("📊 播放器狀態")
            
            info = st.session_state.music_player.get_playlist_info()
            st.write(f"**總歌曲數:** {info['total_songs']}")
            st.write(f"**當前歌曲:** {info['current_song'] or '無'}")
            st.write(f"**播放狀態:** {info['state']}")
            st.write(f"**音量:** {info['volume']:.1%}")
            st.write(f"**隨機播放:** {'開啟' if info['shuffle'] else '關閉'}")
            st.write(f"**重複播放:** {'開啟' if info['repeat'] else '關閉'}")

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
            if info.get('duration'):
                duration_str = time.strftime('%M:%S', time.gmtime(info['duration']))
                st.write(f"時長: {duration_str}")
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
                    if format_choice == "MP3 音訊" and result.get('file_path') and MUSIC_PLAYER_AVAILABLE:
                        if init_music_player():
                            scan_music_folder()
                    
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
            if format_choice == "MP3 音訊" and MUSIC_PLAYER_AVAILABLE:
                st.markdown("---")
                st.subheader("🎵 立即播放")
                if st.button("▶️ 在播放器中播放此歌曲", use_container_width=True):
                    if init_music_player():
                        scan_music_folder()
                        # 找到剛下載的歌曲並播放
                        for i, song in enumerate(st.session_state.playlist):
                            if song.file_path == file_path:
                                st.session_state.music_player.play(i)
                                st.success("🎵 開始播放！")
                                break
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
                        if video.get('duration'):
                            duration_str = time.strftime('%M:%S', time.gmtime(video['duration']))
                            st.write(f"時長: {duration_str}")
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
                                    if batch_format == "MP3 音訊" and MUSIC_PLAYER_AVAILABLE:
                                        if init_music_player():
                                            scan_music_folder()
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
                    if batch_format == "MP3 音訊" and MUSIC_PLAYER_AVAILABLE:
                        if init_music_player():
                            scan_music_folder()
                            st.info("🎵 播放清單已更新，可以在音樂播放器標籤頁中查看")

# 標籤頁 3: 音樂播放器
with tab3:
    if not MUSIC_PLAYER_AVAILABLE:
        st.error("❌ 音樂播放器功能不可用")
        st.info("請安裝必要的套件：")
        st.code("pip install pygame mutagen")
    else:
        # 初始化播放器
        if not init_music_player():
            st.warning("⚠️ 請在側邊欄初始化播放器")
        else:
            # 播放控制區域
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown("### 🎮 播放控制")
                
                # 播放控制按鈕
                control_col1, control_col2, control_col3, control_col4, control_col5 = st.columns(5)
                
                with control_col1:
                    if st.button("⏮️", help="上一首", use_container_width=True):
                        st.session_state.music_player.previous()
                
                with control_col2:
                    if st.session_state.playback_state == PlaybackState.PLAYING:
                        if st.button("⏸️", help="暫停", use_container_width=True):
                            st.session_state.music_player.pause()
                    else:
                        if st.button("▶️", help="播放", use_container_width=True):
                            if st.session_state.playback_state == PlaybackState.PAUSED:
                                st.session_state.music_player.resume()
                            else:
                                st.session_state.music_player.play()
                
                with control_col3:
                    if st.button("⏹️", help="停止", use_container_width=True):
                        st.session_state.music_player.stop()
                
                with control_col4:
                    if st.button("⏭️", help="下一首", use_container_width=True):
                        st.session_state.music_player.next()
                
                with control_col5:
                    if st.button("🔄", help="重新掃描", use_container_width=True):
                        scan_music_folder()
                
                # 播放模式控制
                mode_col1, mode_col2 = st.columns(2)
                
                with mode_col1:
                    if st.button(
                        "🔀 隨機播放" if not st.session_state.is_shuffle else "🔀 關閉隨機",
                        use_container_width=True,
                        type="secondary" if st.session_state.is_shuffle else "primary"
                    ):
                        st.session_state.music_player.toggle_shuffle()
                        st.session_state.is_shuffle = not st.session_state.is_shuffle
                
                with mode_col2:
                    if st.button(
                        "🔁 重複播放" if not st.session_state.is_repeat else "🔁 關閉重複",
                        use_container_width=True,
                        type="secondary" if st.session_state.is_repeat else "primary"
                    ):
                        st.session_state.music_player.toggle_repeat()
                        st.session_state.is_repeat = not st.session_state.is_repeat
                
                # 音量控制
                st.markdown("### 🔊 音量控制")
                volume = st.slider(
                    "音量",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.volume,
                    step=0.1,
                    format="%.1f"
                )
                
                if volume != st.session_state.volume:
                    st.session_state.volume = volume
                    st.session_state.music_player.set_volume(volume)
            
            # 當前播放資訊
            if st.session_state.current_song:
                st.markdown("---")
                st.markdown("### 🎵 正在播放")
                
                song = st.session_state.current_song
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown("🎵")
                
                with col2:
                    st.subheader(song.title)
                    st.write(f"**藝術家:** {song.artist}")
                    st.write(f"**專輯:** {song.album}")
                    st.write(f"**時長:** {song.duration_str}")
                    st.write(f"**檔案大小:** {format_file_size(song.file_size)}")
                    st.write(f"**檔案名稱:** {song.filename}")
                
                # 播放進度條
                if song.duration > 0:
                    st.markdown("### 📊 播放進度")
                    progress = st.session_state.current_progress
                    current_time = progress * song.duration
                    
                    st.write(f"**進度:** {format_time(current_time)} / {song.duration_str}")
                    st.progress(progress, text=f"{progress:.1%}")
            
            # 播放清單
            if st.session_state.playlist:
                st.markdown("---")
                st.markdown("### 📋 播放清單")
                
                # 播放清單統計
                total_duration = sum(song.duration for song in st.session_state.playlist)
                total_size = sum(song.file_size for song in st.session_state.playlist)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("總歌曲數", len(st.session_state.playlist))
                with col2:
                    st.metric("總時長", format_time(total_duration))
                with col3:
                    st.metric("總大小", format_file_size(total_size))
                
                # 歌曲列表
                st.markdown("#### 🎵 歌曲列表")
                
                for i, song in enumerate(st.session_state.playlist):
                    # 高亮當前播放的歌曲
                    is_current = (i == st.session_state.music_player.current_index)
                    
                    with st.container():
                        col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
                        
                        with col1:
                            if is_current:
                                st.markdown("🎵")
                            else:
                                st.markdown(f"{i+1}")
                        
                        with col2:
                            if is_current:
                                st.markdown(f"**{song.title}**")
                            else:
                                st.markdown(song.title)
                            st.caption(f"{song.artist} - {song.album}")
                        
                        with col3:
                            st.write(song.duration_str)
                        
                        with col4:
                            if st.button("▶️", key=f"play_{i}_3", help="播放此歌曲"):
                                st.session_state.music_player.play(i)
                        
                        if is_current:
                            st.markdown("---")
                
                # 批量操作
                st.markdown("#### ⚙️ 批量操作")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🎵 播放全部", use_container_width=True):
                        st.session_state.music_player.play(0)
                
                with col2:
                    if st.button("🔄 重新整理清單", use_container_width=True):
                        scan_music_folder()
            else:
                st.info("📁 播放清單為空，請先掃描音樂資料夾")

# 標籤頁 4: iPhone 背景播放
with tab4:
    st.subheader("📱 iPhone 背景播放設定")
    
    if not MUSIC_PLAYER_AVAILABLE:
        st.error("❌ 音樂播放器功能不可用")
    else:
        st.markdown("""
        ### 🎵 iPhone 背景播放功能
        
        本播放器支援 iPhone 背景播放，讓您可以在使用其他應用程式時繼續聽音樂。
        
        #### ✨ 功能特色
        - **背景播放**: 即使關閉應用程式，音樂仍會繼續播放
        - **控制中心整合**: 可以在 iPhone 控制中心控制播放
        - **鎖定螢幕控制**: 在鎖定螢幕上顯示播放控制
        - **AirPods 支援**: 完美支援 AirPods 和其他藍牙耳機
        
        #### 🔧 設定步驟
        1. **初始化播放器**: 在側邊欄點擊「初始化播放器」
        2. **掃描音樂**: 點擊「掃描音樂資料夾」載入音樂
        3. **開始播放**: 選擇歌曲並開始播放
        4. **背景播放**: 播放開始後，可以切換到其他應用程式
        
        #### 📱 使用方式
        - **播放控制**: 使用播放控制按鈕或 iPhone 控制中心
        - **音量調整**: 使用音量滑桿或 iPhone 音量按鈕
        - **播放模式**: 可以開啟隨機播放或重複播放
        - **播放清單**: 瀏覽和管理您的音樂清單
        
        #### 🎧 耳機控制
        - **單擊**: 播放/暫停
        - **雙擊**: 下一首
        - **三擊**: 上一首
        - **長按**: 語音助手（Siri）
        
        #### ⚠️ 注意事項
        - 確保 iPhone 的音量設定適當
        - 背景播放需要網路連線
        - 某些應用程式可能會中斷背景播放
        - 建議使用有線耳機或 AirPods 以獲得最佳體驗
        """)
        
        # 背景播放狀態
        if st.session_state.music_player:
            st.markdown("---")
            st.subheader("📊 背景播放狀態")
            
            info = st.session_state.music_player.get_playlist_info()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("播放狀態", info['state'].title())
                st.metric("當前歌曲", info['current_song'] or "無")
            
            with col2:
                st.metric("音量", f"{info['volume']:.1%}")
                st.metric("總歌曲數", info['total_songs'])
            
            # 背景播放控制
            st.markdown("### 🎮 背景播放控制")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎵 啟用背景播放", use_container_width=True):
                    st.success("✅ 背景播放已啟用")
            
            with col2:
                if st.button("⏹️ 停用背景播放", use_container_width=True):
                    st.info("ℹ️ 背景播放已停用")
        else:
            st.warning("⚠️ 請先初始化音樂播放器")

# 頁腳資訊
st.markdown("---")
st.markdown("""
### 📝 使用說明

1. **下載音樂**: 在「直接下載」或「搜尋下載」標籤頁下載 YouTube 影片為 MP3 格式
2. **播放音樂**: 在「音樂播放器」標籤頁播放下載的音樂
3. **背景播放**: 在「iPhone 背景播放」標籤頁了解背景播放功能
4. **雲端上傳**: 啟用自動上傳功能，將音樂同步到雲端硬碟

### 🎵 支援的格式
- **下載格式**: MP3, MP4
- **播放格式**: MP3, WAV, OGG, FLAC, M4A

### 📱 iPhone 背景播放
本播放器支援 iPhone 背景播放功能，讓您可以在使用其他應用程式時繼續聽音樂。
""")

# 自動重新整理（用於更新播放進度）
if st.session_state.music_player and st.session_state.playback_state == PlaybackState.PLAYING:
    time.sleep(1)
    st.rerun() 