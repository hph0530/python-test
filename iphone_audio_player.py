#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iPhone 優化音訊播放器
專門解決 iPhone 播放問題
"""

import streamlit as st
from pathlib import Path
import base64
import io
from mutagen import File
from mutagen.mp3 import MP3
import time

# 導入密碼驗證模組
try:
    from password_auth import (
        init_password_session, 
        show_login_page, 
        show_security_info, 
        change_password, 
        show_security_help
    )
    PASSWORD_AUTH_AVAILABLE = True
except ImportError as e:
    PASSWORD_AUTH_AVAILABLE = False

def scan_music_folder():
    """掃描音樂資料夾"""
    downloads_dir = Path("downloads")
    if not downloads_dir.exists():
        return []
    
    music_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac'}
    music_files = []
    
    for file_path in downloads_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in music_extensions:
            music_files.append(file_path)
    
    return sorted(music_files, key=lambda x: x.name)

def get_audio_file_info(file_path):
    """獲取音訊檔案資訊"""
    try:
        # 檔案大小
        file_size = file_path.stat().st_size
        
        # 使用 mutagen 讀取音訊資訊
        audio = File(str(file_path))
        
        if audio is None:
            return {
                'title': file_path.stem,
                'artist': '未知藝術家',
                'album': '未知專輯',
                'duration': 0,
                'file_size': file_size
            }
        
        # 獲取標籤資訊
        title = None
        artist = None
        album = None
        duration = 0
        
        # 嘗試獲取標籤資訊
        if hasattr(audio, 'tags'):
            if audio.tags:
                if 'title' in audio.tags:
                    title = str(audio.tags['title'][0]) if audio.tags['title'] else None
                if 'artist' in audio.tags:
                    artist = str(audio.tags['artist'][0]) if audio.tags['artist'] else None
                if 'album' in audio.tags:
                    album = str(audio.tags['album'][0]) if audio.tags['album'] else None
        
        # 獲取時長
        if hasattr(audio, 'info'):
            duration = audio.info.length if hasattr(audio.info, 'length') else 0
        
        return {
            'title': title or file_path.stem,
            'artist': artist or '未知藝術家',
            'album': album or '未知專輯',
            'duration': duration,
            'file_size': file_size
        }
    except Exception as e:
        return {
            'title': file_path.stem,
            'artist': '未知藝術家',
            'album': '未知專輯',
            'duration': 0,
            'file_size': file_path.stat().st_size
        }

def format_time(seconds: float) -> str:
    """格式化時間"""
    if seconds <= 0:
        return "00:00"
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def format_file_size(size_bytes: int) -> str:
    """格式化檔案大小"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

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

def main():
    # 密碼驗證檢查
    if PASSWORD_AUTH_AVAILABLE:
        init_password_session()
        
        # 檢查是否已登入
        if not st.session_state.get('password_verified', False):
            show_login_page()
            st.stop()  # 完全停止程式執行
    
    st.set_page_config(
        page_title="iPhone 音訊播放器",
        page_icon="🎵",
        layout="wide"
    )
    
    st.title("📱 iPhone 優化音訊播放器")
    st.markdown("專門為 iPhone 設計的音訊播放器，解決播放問題")
    
    # 顯示安全資訊在側邊欄
    if PASSWORD_AUTH_AVAILABLE:
        show_security_info()
        
        # 處理密碼管理功能
        if st.session_state.get('show_change_password', False):
            change_password()
            st.stop()
        
        if st.session_state.get('show_security_help', False):
            show_security_help()
            st.stop()
    
    # 初始化 session state
    if 'music_files' not in st.session_state:
        st.session_state.music_files = []
    if 'selected_file' not in st.session_state:
        st.session_state.selected_file = None
    
    # 掃描音樂資料夾
    if st.button("📁 掃描音樂資料夾", type="primary", use_container_width=True):
        music_files = scan_music_folder()
        st.session_state.music_files = music_files
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
                st.session_state.selected_file = selected_file
                
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
        
        # 主要播放區域
        if st.session_state.selected_file:
            st.markdown("---")
            st.subheader(f"🎵 正在播放: {st.session_state.selected_file.name}")
            
            # 讀取音訊檔案
            try:
                with open(st.session_state.selected_file, "rb") as f:
                    audio_bytes = f.read()
                
                # 獲取 MIME 類型
                mime_type = get_audio_mime_type(st.session_state.selected_file)
                
                # 創建 iPhone 優化播放器
                create_iphone_audio_player(audio_bytes, mime_type, st.session_state.selected_file.name)
                
                # 下載按鈕
                st.markdown("---")
                st.subheader("📥 下載選項")
                
                st.download_button(
                    label="📥 下載音樂檔案",
                    data=audio_bytes,
                    file_name=st.session_state.selected_file.name,
                    mime=mime_type,
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"讀取檔案失敗: {e}")
        
        # 播放清單
        st.markdown("---")
        st.subheader("📋 播放清單")
        
        # 顯示所有音樂檔案
        for i, file_path in enumerate(st.session_state.music_files, 1):
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
                
                with col1:
                    st.write(f"{i}")
                
                with col2:
                    file_info = get_audio_file_info(file_path)
                    st.write(f"**{file_info['title']}**")
                    st.caption(f"{file_info['artist']} • {format_time(file_info['duration'])} • {format_file_size(file_info['file_size'])}")
                
                with col3:
                    if st.button("▶️", key=f"play_{i}", help="播放此歌曲"):
                        st.session_state.selected_file = file_path
                        st.rerun()
                
                with col4:
                    # 下載按鈕
                    try:
                        with open(file_path, "rb") as f:
                            file_bytes = f.read()
                        
                        mime_type = get_audio_mime_type(file_path)
                        st.download_button(
                            label="📥",
                            data=file_bytes,
                            file_name=file_path.name,
                            mime=mime_type,
                            key=f"download_{i}"
                        )
                    except Exception as e:
                        st.error("❌")
                
                st.markdown("---")
    else:
        st.info("📁 請先掃描音樂資料夾或下載一些 MP3 檔案")
        st.markdown("""
        ### 📝 使用說明
        
        1. **下載音樂**: 在 YouTube 下載器標籤頁下載 MP3 檔案
        2. **掃描資料夾**: 點擊「掃描音樂資料夾」按鈕
        3. **選擇音樂**: 在側邊欄選擇要播放的音樂檔案
        4. **播放控制**: 使用 iPhone 優化播放器控制播放
        5. **下載音樂**: 點擊下載按鈕下載音樂檔案
        
        ### 🎵 支援的格式
        - MP3 (.mp3) - 最佳支援
        - M4A (.m4a) - iPhone 原生支援
        - AAC (.aac) - iPhone 原生支援
        - WAV (.wav) - 基本支援
        - OGG (.ogg) - 有限支援
        - FLAC (.flac) - 有限支援
        
        ### 📱 iPhone 優化功能
        - 使用 HTML5 audio 元素
        - 正確的 MIME 類型設定
        - iPhone 特定的播放提示
        - 支援 Safari 瀏覽器
        - 背景播放支援
        """)
    
    # iPhone 使用提示
    st.markdown("---")
    st.subheader("📱 iPhone 使用提示")
    st.markdown("""
    ### 🎯 最佳體驗建議
    
    1. **使用 Safari 瀏覽器**
       - Safari 對音訊播放支援最佳
       - 避免使用 Chrome 或 Firefox
    
    2. **確保設定正確**
       - 開啟音量
       - 允許網站播放音訊
       - 確保網路連線穩定
    
    3. **播放技巧**
       - 點擊播放後等待 2-3 秒
       - 如果無法播放，重新整理頁面
       - 嘗試下載後在音樂 App 中播放
    
    4. **故障排除**
       - 重新啟動 Safari
       - 清除瀏覽器快取
       - 檢查 iOS 版本是否最新
    """)

if __name__ == "__main__":
    main() 