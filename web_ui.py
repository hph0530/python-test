import streamlit as st
from pathlib import Path
import re
import time
import traceback

# 匯入我們重構後的下載器
from youtube_downloader import YouTubeDownloader

# 匯入 yt-dlp 搜尋器
try:
    from yt_dlp_searcher import YtDlpSearcher
    SEARCH_AVAILABLE = True
except ImportError as e:
    st.error(f"❌ 搜尋功能載入失敗: {e}")
    SEARCH_AVAILABLE = False

# 檢查雲端上傳功能是否可用
try:
    from cloud_uploader import CloudUploadManager
    CLOUD_UPLOAD_AVAILABLE = True
except ImportError as e:
    st.warning(f"⚠️ 雲端上傳功能不可用: {e}")
    CLOUD_UPLOAD_AVAILABLE = False

# --- 頁面設定 ---
st.set_page_config(
    page_title="YouTube 多格式下載器",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- 狀態管理 ---
if 'video_info' not in st.session_state:
    st.session_state.video_info = None
if 'download_result' not in st.session_state:
    st.session_state.download_result = None
if 'is_downloading' not in st.session_state:
    st.session_state.is_downloading = False
if 'cloud_services' not in st.session_state:
    st.session_state.cloud_services = []
if 'auto_upload' not in st.session_state:
    st.session_state.auto_upload = False
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'selected_videos' not in st.session_state:
    st.session_state.selected_videos = []

st.title("🎬 YouTube 多格式下載器")
st.markdown("輸入 YouTube 影片網址或搜尋影片，選擇格式，即可輕鬆下載！")

tab1, tab2 = st.tabs(["🔗 直接下載", "🔍 搜尋下載"])

with tab1:
    st.subheader("直接輸入 YouTube 網址下載")
    url = st.text_input("YouTube 影片網址", placeholder="https://www.youtube.com/watch?v=...", key="url_input")
    format_choice = st.radio("選擇下載格式", ("MP4 影片", "MP3 音訊"), horizontal=True, key="format_choice_1")
    
    st.markdown("---")
    st.subheader("☁️ 雲端硬碟上傳設定")
    if CLOUD_UPLOAD_AVAILABLE:
        st.session_state.auto_upload = st.checkbox("啟用自動上傳到雲端硬碟", value=st.session_state.auto_upload, key="auto_upload_1")
        st.info("目前只支援自動上傳到 Google Drive，且會自動依格式分流到指定資料夾。\n\nMP3 會上傳到 folder id: 1n-Y81X-lvha8KP7HxoWd17Chg5O0XN6w\nMP4 會上傳到 folder id: 1JocRza3zPEerZkg2z74ROOigN5XI2aCP")
    else:
        st.warning("⚠️ 雲端上傳功能不可用，只能下載到本地")
        st.session_state.auto_upload = False
    
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
                    
                    if result.get('file_path') and Path(result['file_path']).exists():
                        st.session_state.download_result = {
                            'success': True,
                            'path': result['file_path'],
                            'filename': Path(result['file_path']).name,
                            'upload_result': result.get('upload_result')
                        }
                    else:
                        raise Exception("下載後找不到檔案。")
                        
                except Exception as e:
                    st.session_state.download_result = {
                        'success': False, 
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    }
                finally:
                    st.session_state.is_downloading = False
                    st.rerun()
    
    if st.session_state.download_result:
        result = st.session_state.download_result
        if result['success']:
            st.success(f"✅ **{result['filename']}** 下載成功！")
            
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
                else:
                    for service, service_result in upload_result.items():
                        service_names = {
                            'google_drive': 'Google Drive',
                            'dropbox': 'Dropbox',
                            'onedrive': 'OneDrive'
                        }
                        service_name = service_names.get(service, service)
                        
                        if service_result.get('success'):
                            st.success(f"✅ 已上傳到 {service_name}")
                            if service_result.get('web_link'):
                                st.markdown(f"🔗 [{service_name} 查看檔案]({service_result['web_link']})")
                        else:
                            st.error(f"❌ {service_name} 上傳失敗: {service_result.get('error', '未知錯誤')}")
            
            # 本地下載按鈕
            file_path = result['path']
            try:
                with open(file_path, "rb") as file:
                    st.download_button(
                        label=f"點此下載 {result['filename']}",
                        data=file,
                        file_name=result['filename'],
                        mime="application/octet-stream",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"無法讀取檔案: {e}")
        else:
            st.error(f"❌ 下載失敗: {result['error']}")
            if result.get('traceback'):
                with st.expander("查看詳細錯誤"):
                    st.code(result['traceback'])
            st.warning("如果錯誤與 `ffmpeg` 相關，請確保已正確安裝並設定環境變數。")

with tab2:
    st.subheader("搜尋 YouTube 影片並下載")
    
    if not SEARCH_AVAILABLE:
        st.error("❌ 搜尋功能不可用，請確認 yt-dlp 已安裝")
        st.code("pip install yt-dlp")
    else:
        search_query = st.text_input("搜尋關鍵字", placeholder="輸入要搜尋的影片關鍵字", key="search_input")
        
        if st.button("🔍 搜尋影片", type="primary", use_container_width=True, key="search_btn"):
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
            batch_format = st.radio("選擇下載格式", ("MP4 影片", "MP3 音訊"), horizontal=True, key="batch_format")
            if CLOUD_UPLOAD_AVAILABLE:
                batch_auto_upload = st.checkbox("啟用自動上傳到雲端硬碟", value=st.session_state.auto_upload, key="batch_auto_upload")
            else:
                st.warning("⚠️ 雲端上傳功能不可用")
                batch_auto_upload = False
            
            # 顯示影片列表
            st.markdown("### 🎬 選擇要下載的影片")
            
            # 全選/取消全選
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("全選", key="select_all"):
                    st.session_state.selected_videos = [i for i in range(len(st.session_state.search_results))]
                    st.rerun()
                if st.button("取消全選", key="deselect_all"):
                    st.session_state.selected_videos = []
                    st.rerun()
            
            # 顯示每個影片
            for i, video in enumerate(st.session_state.search_results):
                with st.container():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    
                    with col1:
                        if video.get('thumbnail'):
                            st.image(video['thumbnail'], width=120)
                    
                    with col2:
                        st.markdown(f"**{video.get('title', '無標題')}**")
                        st.caption(f"由 {video.get('uploader', '未知上傳者')} 上傳")
                        st.write(f"⏱️ 時長: {video.get('duration', '未知')}")
                        st.write(f"👁️ 觀看次數: {video.get('view_count', 0):,}")
                        st.write(f"📅 上傳時間: {video.get('upload_date', '未知')}")
                        
                        if video.get('description'):
                            st.caption(f"📝 {video['description']}")
                    
                    with col3:
                        is_selected = st.checkbox(
                            "選擇下載",
                            value=i in st.session_state.selected_videos,
                            key=f"select_{i}"
                        )
                        
                        if is_selected and i not in st.session_state.selected_videos:
                            st.session_state.selected_videos.append(i)
                        elif not is_selected and i in st.session_state.selected_videos:
                            st.session_state.selected_videos.remove(i)
                
                st.markdown("---")
            
            # 批量下載按鈕
            if st.session_state.selected_videos:
                st.markdown("### 🚀 批量下載")
                st.info(f"已選擇 {len(st.session_state.selected_videos)} 個影片進行下載")
                
                if st.button(f"開始批量下載 {batch_format.split(' ')[0]}", type="primary", use_container_width=True, key="batch_download_btn"):
                    selected_videos = [st.session_state.search_results[i] for i in st.session_state.selected_videos]
                    
                    progress_bar = st.progress(0, text="準備開始批量下載...")
                    status_text = st.empty()
                    
                    downloader = YouTubeDownloader(
                        auto_upload=batch_auto_upload,
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
                            
                            results.append({
                                'title': video.get('title', '未知標題'),
                                'success': result.get('file_path') and Path(result['file_path']).exists(),
                                'file_path': result.get('file_path'),
                                'upload_result': result.get('upload_result'),
                                'error': result.get('error')
                            })
                            
                        except Exception as e:
                            results.append({
                                'title': video.get('title', '未知標題'),
                                'success': False,
                                'error': str(e)
                            })
                    
                    # 顯示批量下載結果
                    st.markdown("### 📊 批量下載結果")
                    success_count = sum(1 for r in results if r['success'])
                    st.success(f"✅ 成功下載 {success_count}/{len(results)} 個檔案")
                    
                    for result in results:
                        if result['success']:
                            st.success(f"✅ {result['title']}")
                            if result.get('upload_result'):
                                st.caption("☁️ 已上傳到雲端硬碟")
                        else:
                            st.error(f"❌ {result['title']}: {result.get('error', '未知錯誤')}")

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