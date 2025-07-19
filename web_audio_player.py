#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
網頁音訊播放器
使用 Streamlit 內建音訊播放器播放音樂
"""

import streamlit as st
from pathlib import Path
import os

def main():
    st.set_page_config(
        page_title="🎵 網頁音訊播放器",
        page_icon="🎵",
        layout="wide"
    )
    
    st.title("🎵 網頁音訊播放器")
    st.markdown("使用 Streamlit 內建音訊播放器播放音樂檔案")
    
    # 掃描音樂檔案
    downloads_dir = Path("downloads")
    if not downloads_dir.exists():
        st.error("❌ downloads 資料夾不存在")
        return
    
    # 尋找音樂檔案
    supported_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.m4a'}
    music_files = []
    
    for file_path in downloads_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            music_files.append(file_path)
    
    if not music_files:
        st.warning("⚠️ 沒有找到音樂檔案")
        st.info("請先在 downloads 資料夾中放入一些音樂檔案")
        return
    
    st.success(f"✅ 找到 {len(music_files)} 個音樂檔案")
    
    # 側邊欄：檔案選擇
    with st.sidebar:
        st.header("📁 選擇音樂檔案")
        
        # 檔案選擇器
        selected_file = st.selectbox(
            "選擇要播放的音樂檔案",
            options=music_files,
            format_func=lambda x: x.name
        )
        
        if selected_file:
            # 顯示檔案資訊
            st.subheader("📋 檔案資訊")
            file_size = selected_file.stat().st_size
            st.write(f"**檔案名稱:** {selected_file.name}")
            st.write(f"**檔案大小:** {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
            st.write(f"**檔案格式:** {selected_file.suffix.upper()}")
            
            # 播放選項
            st.subheader("🎮 播放選項")
            autoplay = st.checkbox("自動播放", value=False)
    
    # 主要內容區域
    if selected_file:
        st.markdown("---")
        st.subheader(f"🎵 正在播放: {selected_file.name}")
        
        # 使用 Streamlit 內建音訊播放器
        with open(selected_file, "rb") as f:
            audio_bytes = f.read()
        
        st.audio(audio_bytes, format=f'audio/{selected_file.suffix[1:]}')
        
        # 下載按鈕
        st.markdown("---")
        st.subheader("📥 下載選項")
        
        st.download_button(
            label="📥 下載音樂檔案",
            data=audio_bytes,
            file_name=selected_file.name,
            mime=f"audio/{selected_file.suffix[1:]}"
        )
    
    # 播放清單
    st.markdown("---")
    st.subheader("📋 播放清單")
    
    # 顯示所有音樂檔案
    for i, file_path in enumerate(music_files, 1):
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
            
            with col1:
                st.write(f"{i}")
            
            with col2:
                st.write(f"**{file_path.name}**")
                file_size = file_path.stat().st_size
                st.caption(f"{file_size/1024/1024:.1f} MB • {file_path.suffix.upper()}")
            
            with col3:
                if st.button("▶️", key=f"play_{i}", help="播放此歌曲"):
                    # 更新選擇的檔案
                    st.session_state.selected_file = file_path
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
            
            st.markdown("---")
    
    # 使用說明
    st.markdown("---")
    st.markdown("""
    ### 📝 使用說明
    
    1. **選擇音樂**: 在側邊欄選擇要播放的音樂檔案
    2. **播放控制**: 使用內建音訊播放器控制播放
    3. **下載音樂**: 點擊下載按鈕下載音樂檔案
    4. **播放清單**: 瀏覽所有可用的音樂檔案
    
    ### 🎵 支援的格式
    - MP3 (.mp3)
    - WAV (.wav)
    - OGG (.ogg)
    - FLAC (.flac)
    - M4A (.m4a)
    
    ### ⚠️ 注意事項
    - 某些瀏覽器可能不支援某些音訊格式
    - 大檔案可能需要較長時間載入
    - 建議使用現代瀏覽器以獲得最佳體驗
    - 如果沒有聲音，請檢查瀏覽器的音訊設定
    """)

if __name__ == "__main__":
    main() 