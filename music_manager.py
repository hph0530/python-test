#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音樂檔案管理工具
包含刪除、重新整理和檔案管理功能
"""

import streamlit as st
from pathlib import Path
import os
import shutil
from mutagen import File
import time

def scan_music_folder():
    """掃描音樂資料夾"""
    downloads_dir = Path("downloads")
    if not downloads_dir.exists():
        return []
    
    music_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.webm'}
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

def delete_file(file_path):
    """刪除檔案"""
    try:
        file_path.unlink()
        return True, f"成功刪除: {file_path.name}"
    except Exception as e:
        return False, f"刪除失敗: {e}"

def move_to_trash(file_path):
    """移動檔案到垃圾桶"""
    try:
        trash_dir = Path("downloads/trash")
        trash_dir.mkdir(exist_ok=True)
        
        new_path = trash_dir / file_path.name
        # 如果檔案已存在，添加時間戳
        if new_path.exists():
            timestamp = int(time.time())
            new_path = trash_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        
        shutil.move(str(file_path), str(new_path))
        return True, f"已移動到垃圾桶: {file_path.name}"
    except Exception as e:
        return False, f"移動失敗: {e}"

def clean_trash():
    """清空垃圾桶"""
    try:
        trash_dir = Path("downloads/trash")
        if trash_dir.exists():
            shutil.rmtree(trash_dir)
            trash_dir.mkdir(exist_ok=True)
        return True, "垃圾桶已清空"
    except Exception as e:
        return False, f"清空垃圾桶失敗: {e}"

def get_folder_stats():
    """獲取資料夾統計資訊"""
    downloads_dir = Path("downloads")
    if not downloads_dir.exists():
        return {"total_files": 0, "total_size": 0, "total_duration": 0}
    
    music_files = scan_music_folder()
    total_size = sum(f.stat().st_size for f in music_files)
    total_duration = sum(get_audio_file_info(f)['duration'] for f in music_files)
    
    return {
        "total_files": len(music_files),
        "total_size": total_size,
        "total_duration": total_duration
    }

def main():
    st.set_page_config(
        page_title="音樂檔案管理",
        page_icon="🎵",
        layout="wide"
    )
    
    st.title("🎵 音樂檔案管理工具")
    st.markdown("管理您的音樂檔案，包含刪除、重新整理和檔案資訊")
    
    # 初始化 session state
    if 'music_files' not in st.session_state:
        st.session_state.music_files = []
    if 'selected_files' not in st.session_state:
        st.session_state.selected_files = []
    
    # 側邊欄：統計資訊
    with st.sidebar:
        st.header("📊 統計資訊")
        
        if st.button("🔄 重新整理統計", type="primary", use_container_width=True):
            stats = get_folder_stats()
            st.session_state.stats = stats
        
        if 'stats' in st.session_state:
            stats = st.session_state.stats
            st.metric("總檔案數", stats["total_files"])
            st.metric("總大小", format_file_size(stats["total_size"]))
            st.metric("總時長", format_time(stats["total_duration"]))
        
        st.markdown("---")
        st.header("🗑️ 垃圾桶管理")
        
        if st.button("🗑️ 清空垃圾桶", use_container_width=True):
            success, message = clean_trash()
            if success:
                st.success(message)
            else:
                st.error(message)
    
    # 主要內容區域
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📁 掃描音樂資料夾")
        if st.button("🔍 掃描音樂檔案", type="primary", use_container_width=True):
            music_files = scan_music_folder()
            st.session_state.music_files = music_files
            st.success(f"✅ 掃描完成，找到 {len(music_files)} 個音樂檔案")
    
    with col2:
        st.subheader("⚙️ 批量操作")
        if st.session_state.music_files:
            col2a, col2b = st.columns(2)
            with col2a:
                if st.button("🗑️ 刪除選中檔案", use_container_width=True):
                    if st.session_state.selected_files:
                        deleted_count = 0
                        for file_path in st.session_state.selected_files:
                            success, message = delete_file(file_path)
                            if success:
                                deleted_count += 1
                        st.success(f"✅ 成功刪除 {deleted_count} 個檔案")
                        # 重新掃描
                        music_files = scan_music_folder()
                        st.session_state.music_files = music_files
                        st.session_state.selected_files = []
                        st.rerun()
                    else:
                        st.warning("請先選擇要刪除的檔案")
            
            with col2b:
                if st.button("📦 移動到垃圾桶", use_container_width=True):
                    if st.session_state.selected_files:
                        moved_count = 0
                        for file_path in st.session_state.selected_files:
                            success, message = move_to_trash(file_path)
                            if success:
                                moved_count += 1
                        st.success(f"✅ 成功移動 {moved_count} 個檔案到垃圾桶")
                        # 重新掃描
                        music_files = scan_music_folder()
                        st.session_state.music_files = music_files
                        st.session_state.selected_files = []
                        st.rerun()
                    else:
                        st.warning("請先選擇要移動的檔案")
    
    # 顯示音樂檔案列表
    if st.session_state.music_files:
        st.markdown("---")
        st.subheader("📋 音樂檔案列表")
        
        # 全選/取消全選
        col_select, col_info = st.columns([1, 3])
        with col_select:
            if st.button("全選", key="select_all_mgr"):
                st.session_state.selected_files = st.session_state.music_files.copy()
                st.rerun()
            if st.button("取消全選", key="deselect_all_mgr"):
                st.session_state.selected_files = []
                st.rerun()
        
        with col_info:
            if st.session_state.selected_files:
                st.info(f"已選擇 {len(st.session_state.selected_files)} 個檔案")
        
        # 顯示檔案列表
        for i, file_path in enumerate(st.session_state.music_files, 1):
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([0.5, 3, 1, 1, 1])
                
                with col1:
                    is_selected = file_path in st.session_state.selected_files
                    if st.checkbox(f"{i}", value=is_selected, key=f"select_{i}_mgr"):
                        if file_path not in st.session_state.selected_files:
                            st.session_state.selected_files.append(file_path)
                    else:
                        if file_path in st.session_state.selected_files:
                            st.session_state.selected_files.remove(file_path)
                
                with col2:
                    file_info = get_audio_file_info(file_path)
                    st.write(f"**{file_info['title']}**")
                    st.caption(f"{file_info['artist']} • {format_time(file_info['duration'])} • {format_file_size(file_info['file_size'])}")
                    st.caption(f"檔案: {file_path.name}")
                
                with col3:
                    if st.button("🗑️", key=f"delete_{i}_mgr", help="直接刪除"):
                        success, message = delete_file(file_path)
                        if success:
                            st.success("✅")
                            # 重新掃描
                            music_files = scan_music_folder()
                            st.session_state.music_files = music_files
                            st.rerun()
                        else:
                            st.error("❌")
                
                with col4:
                    if st.button("📦", key=f"trash_{i}_mgr", help="移動到垃圾桶"):
                        success, message = move_to_trash(file_path)
                        if success:
                            st.success("✅")
                            # 重新掃描
                            music_files = scan_music_folder()
                            st.session_state.music_files = music_files
                            st.rerun()
                        else:
                            st.error("❌")
                
                with col5:
                    # 下載按鈕
                    try:
                        with open(file_path, "rb") as f:
                            file_bytes = f.read()
                        
                        st.download_button(
                            label="📥",
                            data=file_bytes,
                            file_name=file_path.name,
                            mime="audio/mpeg" if file_path.suffix.lower() == '.mp3' else "audio/mp4",
                            key=f"download_{i}_mgr"
                        )
                    except Exception as e:
                        st.error("❌")
                
                st.markdown("---")
    else:
        st.info("📁 沒有找到音樂檔案，請先下載一些音樂或掃描資料夾")
    
    # 垃圾桶內容
    trash_dir = Path("downloads/trash")
    if trash_dir.exists() and any(trash_dir.iterdir()):
        st.markdown("---")
        st.subheader("🗑️ 垃圾桶內容")
        
        trash_files = list(trash_dir.iterdir())
        for i, file_path in enumerate(trash_files, 1):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"{i}. {file_path.name}")
                st.caption(f"大小: {format_file_size(file_path.stat().st_size)}")
            
            with col2:
                if st.button("🔄 還原", key=f"restore_{i}"):
                    try:
                        new_path = Path("downloads") / file_path.name
                        if new_path.exists():
                            timestamp = int(time.time())
                            new_path = Path("downloads") / f"{file_path.stem}_{timestamp}{file_path.suffix}"
                        shutil.move(str(file_path), str(new_path))
                        st.success("✅ 已還原")
                        st.rerun()
                    except Exception as e:
                        st.error(f"還原失敗: {e}")
            
            with col3:
                if st.button("🗑️ 永久刪除", key=f"perm_delete_{i}"):
                    try:
                        file_path.unlink()
                        st.success("✅ 已永久刪除")
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗: {e}")

if __name__ == "__main__":
    main() 