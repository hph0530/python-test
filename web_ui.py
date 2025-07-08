import streamlit as st
from pathlib import Path
import re
import time

# 匯入我們重構後的下載器
from youtube_downloader import YouTubeDownloader

# --- 頁面設定 ---
st.set_page_config(
    page_title="YouTube 多格式下載器",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- 狀態管理 ---
# Streamlit 每次互動都會重跑腳本，所以需要用 st.session_state 來保存狀態
if 'video_info' not in st.session_state:
    st.session_state.video_info = None
if 'download_result' not in st.session_state:
    st.session_state.download_result = None
if 'is_downloading' not in st.session_state:
    st.session_state.is_downloading = False

# --- 介面 ---
st.title("🎬 YouTube 多格式下載器")
st.markdown("輸入 YouTube 影片網址，選擇格式，即可輕鬆下載！")

# --- 輸入區 ---
url = st.text_input("YouTube 影片網址", placeholder="https://www.youtube.com/watch?v=...")
format_choice = st.radio("選擇下載格式", ("MP4 影片", "MP3 音訊"), horizontal=True)

# 觸發影片資訊獲取
if url:
    # 簡單的 URL 驗證
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
                st.error(f"發生錯誤: {e}")
                st.session_state.video_info = None
    else:
        st.warning("請輸入有效的 YouTube 網址。")

# --- 顯示影片資訊 ---
if st.session_state.video_info:
    info = st.session_state.video_info
    col1, col2 = st.columns([1, 2])
    with col1:
        if info['thumbnail']:
            st.image(info['thumbnail'])
    with col2:
        st.subheader(info['title'])
        st.caption(f"由 {info['uploader']} 上傳")
        duration_str = time.strftime('%M:%S', time.gmtime(info['duration']))
        st.write(f"時長: {duration_str}")
        st.write(f"觀看次數: {info.get('view_count', 0):,}")

# --- 下載按鈕 ---
if st.session_state.video_info:
    if st.button(f"開始下載 {format_choice.split(' ')[0]}", type="primary", use_container_width=True, disabled=st.session_state.is_downloading):
        st.session_state.is_downloading = True
        st.session_state.download_result = None
        
        progress_bar = st.progress(0, text="準備開始下載...")
        status_text = st.empty()

        def progress_hook(d):
            if d['status'] == 'downloading':
                # 提取進度百分比
                percent_str = d.get('_percent_str', '0.0%')
                percent = float(re.findall(r"(\d+\.?\d*)%", percent_str)[0])
                progress_bar.progress(int(percent), text=f"下載中... {percent:.1f}%")
            elif d['status'] == 'finished':
                progress_bar.progress(100, text="下載完成，正在進行後處理...")

        try:
            downloader = YouTubeDownloader()
            downloader.add_progress_hook(progress_hook)
            
            download_func = downloader.download_mp4 if format_choice == "MP4 影片" else downloader.download_mp3
            filepath = download_func(url)
            
            if filepath and Path(filepath).exists():
                st.session_state.download_result = {
                    'success': True,
                    'path': filepath,
                    'filename': Path(filepath).name
                }
            else:
                raise Exception("下載後找不到檔案。")

        except Exception as e:
            st.session_state.download_result = {'success': False, 'error': str(e)}
        
        st.session_state.is_downloading = False
        # 強制重跑一次以顯示下載結果
        st.rerun()

# --- 顯示下載結果 ---
if st.session_state.download_result:
    result = st.session_state.download_result
    if result['success']:
        st.success(f"✅ **{result['filename']}** 下載成功！")
        
        file_path = result['path']
        with open(file_path, "rb") as file:
            st.download_button(
                label=f"點此下載 {result['filename']}",
                data=file,
                file_name=result['filename'],
                mime="application/octet-stream",
                use_container_width=True
            )
    else:
        st.error(f"❌ 下載失敗: {result['error']}")
        st.warning("如果錯誤與 `ffmpeg` 相關，請確保已正確安裝並設定環境變數。")

# --- 側邊欄 ---
st.sidebar.header("關於")
st.sidebar.info(
    "這是一個使用 yt-dlp 和 Streamlit 打造的 YouTube 影片/音訊下載器。"
    "專為教學和方便使用而設計。"
)
st.sidebar.header("注意事項")
st.sidebar.warning(
    "請尊重版權，僅下載您有權觀看的內容。"
    "下載私人影片或受地區限制的影片可能會失敗。"
)
st.sidebar.header("FFmpeg")
st.sidebar.info(
    "下載 MP3 或高品質的 MP4 需要 FFmpeg。"
    "如果遇到問題，請確保您已安裝 FFmpeg 並將其加入系統 PATH。"
) 