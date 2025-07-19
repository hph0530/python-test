#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音樂播放器模組
支援從指定資料夾播放音樂、控制功能，以及 iPhone 背景播放
"""

import os
import time
import threading
import logging
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json

# 音訊處理相關套件
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    from mutagen import File
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PlaybackState(Enum):
    """播放狀態枚舉"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"

@dataclass
class Song:
    """歌曲資訊類別"""
    file_path: str
    title: str
    artist: str
    album: str
    duration: float
    file_size: int
    
    @property
    def filename(self) -> str:
        """獲取檔案名稱"""
        return Path(self.file_path).name
    
    @property
    def duration_str(self) -> str:
        """獲取格式化的時長字串"""
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return f"{minutes:02d}:{seconds:02d}"

class MusicPlayer:
    """音樂播放器核心類別"""
    
    def __init__(self, music_folder: str = "downloads"):
        """
        初始化音樂播放器
        
        Args:
            music_folder: 音樂檔案資料夾路徑
        """
        self.music_folder = Path(music_folder)
        self.music_folder.mkdir(exist_ok=True)
        
        # 播放器狀態
        self.current_song: Optional[Song] = None
        self.playlist: List[Song] = []
        self.current_index: int = -1
        self.state = PlaybackState.STOPPED
        self.volume = 0.7
        self.is_shuffle = False
        self.is_repeat = False
        
        # 播放控制
        self._pygame_initialized = False
        self._play_thread = None
        self._stop_event = threading.Event()
        
        # 回調函數
        self.on_song_change: Optional[Callable[[Song], None]] = None
        self.on_state_change: Optional[Callable[[PlaybackState], None]] = None
        self.on_progress: Optional[Callable[[float], None]] = None
        
        # 初始化 pygame
        if PYGAME_AVAILABLE:
            self._init_pygame()
    
    def _init_pygame(self):
        """初始化 pygame 音訊系統"""
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
            self._pygame_initialized = True
            logging.info("Pygame 音訊系統初始化成功")
        except Exception as e:
            logging.error(f"Pygame 初始化失敗: {e}")
            self._pygame_initialized = False
    
    def scan_music_folder(self) -> List[Song]:
        """
        掃描音樂資料夾，獲取所有支援的音樂檔案
        
        Returns:
            歌曲列表
        """
        supported_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.m4a'}
        songs = []
        
        if not self.music_folder.exists():
            logging.warning(f"音樂資料夾不存在: {self.music_folder}")
            return songs
        
        for file_path in self.music_folder.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    song = self._extract_song_info(file_path)
                    if song:
                        songs.append(song)
                except Exception as e:
                    logging.error(f"無法讀取歌曲資訊 {file_path}: {e}")
        
        # 按檔案名稱排序
        songs.sort(key=lambda x: x.filename.lower())
        self.playlist = songs
        logging.info(f"掃描完成，找到 {len(songs)} 首歌曲")
        return songs
    
    def _extract_song_info(self, file_path: Path) -> Optional[Song]:
        """
        從音樂檔案中提取歌曲資訊
        
        Args:
            file_path: 音樂檔案路徑
            
        Returns:
            歌曲資訊物件
        """
        try:
            file_size = file_path.stat().st_size
            
            # 預設資訊
            title = file_path.stem
            artist = "未知藝術家"
            album = "未知專輯"
            duration = 0.0
            
            # 嘗試使用 mutagen 讀取詳細資訊
            if MUTAGEN_AVAILABLE:
                try:
                    audio = File(str(file_path))
                    if audio is not None:
                        # 讀取時長
                        if hasattr(audio, 'info') and hasattr(audio.info, 'length'):
                            duration = audio.info.length
                        
                        # 讀取 ID3 標籤
                        if hasattr(audio, 'tags') and audio.tags:
                            if 'TIT2' in audio.tags:
                                title = str(audio.tags['TIT2'][0])
                            if 'TPE1' in audio.tags:
                                artist = str(audio.tags['TPE1'][0])
                            if 'TALB' in audio.tags:
                                album = str(audio.tags['TALB'][0])
                except Exception as e:
                    logging.debug(f"無法讀取 ID3 標籤 {file_path}: {e}")
            
            # 如果沒有時長資訊，嘗試使用 pygame 獲取
            if duration == 0.0 and self._pygame_initialized:
                try:
                    sound = pygame.mixer.Sound(str(file_path))
                    duration = sound.get_length()
                except Exception as e:
                    logging.debug(f"無法獲取時長 {file_path}: {e}")
            
            return Song(
                file_path=str(file_path),
                title=title,
                artist=artist,
                album=album,
                duration=duration,
                file_size=file_size
            )
            
        except Exception as e:
            logging.error(f"提取歌曲資訊失敗 {file_path}: {e}")
            return None
    
    def play(self, song_index: Optional[int] = None):
        """
        播放歌曲
        
        Args:
            song_index: 歌曲索引，如果為 None 則播放當前歌曲
        """
        if not self._pygame_initialized:
            logging.error("Pygame 未初始化，無法播放")
            return
        
        if not self.playlist:
            logging.warning("播放清單為空")
            return
        
        # 設定要播放的歌曲
        if song_index is not None:
            if 0 <= song_index < len(self.playlist):
                self.current_index = song_index
            else:
                logging.error(f"無效的歌曲索引: {song_index}")
                return
        
        if self.current_index < 0:
            self.current_index = 0
        
        # 停止當前播放
        self.stop()
        
        # 開始播放新歌曲
        self.current_song = self.playlist[self.current_index]
        self.state = PlaybackState.PLAYING
        
        # 啟動播放執行緒
        self._stop_event.clear()
        self._play_thread = threading.Thread(target=self._play_song)
        self._play_thread.daemon = True
        self._play_thread.start()
        
        # 觸發回調
        if self.on_song_change:
            self.on_song_change(self.current_song)
        if self.on_state_change:
            self.on_state_change(self.state)
        
        logging.info(f"開始播放: {self.current_song.title}")
    
    def _play_song(self):
        """在背景執行緒中播放歌曲"""
        try:
            # 載入並播放歌曲
            pygame.mixer.music.load(self.current_song.file_path)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            
            # 監控播放進度
            start_time = time.time()
            while pygame.mixer.music.get_busy() and not self._stop_event.is_set():
                if self.on_progress and self.current_song.duration > 0:
                    current_time = time.time() - start_time
                    progress = min(current_time / self.current_song.duration, 1.0)
                    self.on_progress(progress)
                time.sleep(0.1)
            
            # 播放結束後的處理
            if not self._stop_event.is_set():
                self._handle_song_end()
                
        except Exception as e:
            logging.error(f"播放歌曲時發生錯誤: {e}")
            self.state = PlaybackState.STOPPED
            if self.on_state_change:
                self.on_state_change(self.state)
    
    def _handle_song_end(self):
        """處理歌曲播放結束"""
        if self.is_repeat:
            # 重複播放當前歌曲
            self.play()
        else:
            # 播放下一首
            self.next()
    
    def pause(self):
        """暫停播放"""
        if self.state == PlaybackState.PLAYING:
            pygame.mixer.music.pause()
            self.state = PlaybackState.PAUSED
            if self.on_state_change:
                self.on_state_change(self.state)
            logging.info("播放已暫停")
    
    def resume(self):
        """恢復播放"""
        if self.state == PlaybackState.PAUSED:
            pygame.mixer.music.unpause()
            self.state = PlaybackState.PLAYING
            if self.on_state_change:
                self.on_state_change(self.state)
            logging.info("播放已恢復")
    
    def stop(self):
        """停止播放"""
        self._stop_event.set()
        pygame.mixer.music.stop()
        self.state = PlaybackState.STOPPED
        if self.on_state_change:
            self.on_state_change(self.state)
        logging.info("播放已停止")
    
    def next(self):
        """播放下一首歌曲"""
        if not self.playlist:
            return
        
        if self.is_shuffle:
            # 隨機播放
            import random
            next_index = random.randint(0, len(self.playlist) - 1)
        else:
            # 順序播放
            next_index = (self.current_index + 1) % len(self.playlist)
        
        self.play(next_index)
    
    def previous(self):
        """播放上一首歌曲"""
        if not self.playlist:
            return
        
        if self.is_shuffle:
            # 隨機播放
            import random
            prev_index = random.randint(0, len(self.playlist) - 1)
        else:
            # 順序播放
            prev_index = (self.current_index - 1) % len(self.playlist)
        
        self.play(prev_index)
    
    def set_volume(self, volume: float):
        """
        設定音量
        
        Args:
            volume: 音量值 (0.0 - 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
        logging.info(f"音量設定為: {self.volume:.2f}")
    
    def seek(self, position: float):
        """
        跳轉到指定位置
        
        Args:
            position: 位置百分比 (0.0 - 1.0)
        """
        if self.current_song and self.current_song.duration > 0:
            target_time = position * self.current_song.duration
            # 注意：pygame 不支援直接跳轉，這裡只是記錄位置
            logging.info(f"跳轉到: {target_time:.2f}s")
    
    def toggle_shuffle(self):
        """切換隨機播放模式"""
        self.is_shuffle = not self.is_shuffle
        logging.info(f"隨機播放: {'開啟' if self.is_shuffle else '關閉'}")
    
    def toggle_repeat(self):
        """切換重複播放模式"""
        self.is_repeat = not self.is_repeat
        logging.info(f"重複播放: {'開啟' if self.is_repeat else '關閉'}")
    
    def get_current_progress(self) -> float:
        """獲取當前播放進度"""
        if not self.current_song or self.current_song.duration <= 0:
            return 0.0
        
        try:
            # 嘗試獲取當前播放位置
            # 注意：pygame 不提供直接獲取當前位置的方法
            return 0.0
        except:
            return 0.0
    
    def get_playlist_info(self) -> Dict:
        """獲取播放清單資訊"""
        return {
            'total_songs': len(self.playlist),
            'current_index': self.current_index,
            'current_song': self.current_song.title if self.current_song else None,
            'state': self.state.value,
            'volume': self.volume,
            'shuffle': self.is_shuffle,
            'repeat': self.is_repeat
        }
    
    def cleanup(self):
        """清理資源"""
        self.stop()
        if self._pygame_initialized:
            pygame.mixer.quit()
            self._pygame_initialized = False

class iPhoneBackgroundPlayer:
    """iPhone 背景播放支援類別"""
    
    def __init__(self, player: MusicPlayer):
        """
        初始化 iPhone 背景播放支援
        
        Args:
            player: 音樂播放器實例
        """
        self.player = player
        self._setup_background_playback()
    
    def _setup_background_playback(self):
        """設定背景播放"""
        try:
            # 設定音訊會話模式，支援背景播放
            if PYGAME_AVAILABLE:
                # 在 iOS 上，pygame 會自動處理背景播放
                # 但我們可以設定一些額外的選項
                os.environ['SDL_AUDIODRIVER'] = 'coreaudio'
                logging.info("iPhone 背景播放支援已啟用")
        except Exception as e:
            logging.error(f"設定背景播放失敗: {e}")
    
    def enable_background_playback(self):
        """啟用背景播放"""
        # 在 iOS 上，這通常需要特殊的設定
        # 這裡我們只是記錄狀態
        logging.info("背景播放已啟用")
    
    def disable_background_playback(self):
        """停用背景播放"""
        logging.info("背景播放已停用")

def create_music_player(music_folder: str = "downloads") -> MusicPlayer:
    """
    創建音樂播放器實例
    
    Args:
        music_folder: 音樂檔案資料夾路徑
        
    Returns:
        音樂播放器實例
    """
    if not PYGAME_AVAILABLE:
        raise ImportError("需要安裝 pygame 套件: pip install pygame")
    
    player = MusicPlayer(music_folder)
    return player 