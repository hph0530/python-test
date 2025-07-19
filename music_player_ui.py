#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音樂播放器網頁介面
使用 Streamlit 創建友善的音樂播放器介面
"""

import streamlit as st
import time
import threading
from pathlib import Path
from typing import Optional

# 匯入音樂播放器模組
try:
    from music_player import MusicPlayer, PlaybackState, Song, create_music_player
    MUSIC_PLAYER_AVAILABLE = True
except ImportError as e:
    st.error(f"❌ 音樂播放器模組載入失敗: {e}")
    MUSIC_PLAYER_AVAILABLE = False

# --- 頁面設定 ---
st.set_page_config(
    page_title="🎵 音樂播放器",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 狀態管理 ---
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
if 'music_folder' not in st.session_state:
    st.session_state.music_folder = "downloads"

def init_music_player():
    """初始化音樂播放器"""
    if not MUSIC_PLAYER_AVAILABLE:
        return False
    
    try:
        if st.session_state.music_player is None:
            st.session_state.music_player = create_music_player(st.session_state.music_folder)
            
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
st.title("🎵 音樂播放器")
st.markdown("播放您下載的音樂檔案，支援播放控制、播放清單管理等功能")

# 側邊欄設定
with st.sidebar:
    st.header("⚙️ 設定")
    
    # 音樂資料夾設定
    music_folder = st.text_input(
        "音樂資料夾路徑",
        value=st.session_state.music_folder,
        help="指定包含音樂檔案的資料夾路徑"
    )
    
    if music_folder != st.session_state.music_folder:
        st.session_state.music_folder = music_folder
        st.session_state.music_player = None  # 重新初始化播放器
    
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

# 主要內容區域
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
                # 這裡可以放置專輯封面（如果有）
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
                        if st.button("▶️", key=f"play_{i}", help="播放此歌曲"):
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

# 頁腳資訊
st.markdown("---")
st.markdown("""
### 📝 使用說明

1. **初始化播放器**: 在側邊欄點擊「初始化播放器」按鈕
2. **掃描音樂**: 點擊「掃描音樂資料夾」來載入音樂檔案
3. **播放控制**: 使用播放控制按鈕來控制播放
4. **播放模式**: 可以開啟隨機播放或重複播放
5. **音量控制**: 使用滑桿調整音量大小

### 🎵 支援的格式
- MP3 (.mp3)
- WAV (.wav)
- OGG (.ogg)
- FLAC (.flac)
- M4A (.m4a)

### 📱 iPhone 背景播放
本播放器支援 iPhone 背景播放功能，讓您可以在使用其他應用程式時繼續聽音樂。
""")

# 自動重新整理（用於更新播放進度）
if st.session_state.music_player and st.session_state.playback_state == PlaybackState.PLAYING:
    time.sleep(1)
    st.rerun() 