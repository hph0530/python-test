#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音樂播放器測試腳本
測試音樂播放器的各項功能
"""

import os
import time
from pathlib import Path

def test_music_player():
    """測試音樂播放器功能"""
    print("🎵 音樂播放器測試")
    print("=" * 60)
    
    try:
        # 檢查必要套件
        print("🔍 檢查必要套件...")
        
        try:
            import pygame
            print("✅ pygame 已安裝")
        except ImportError:
            print("❌ pygame 未安裝，請執行: pip install pygame")
            return False
        
        try:
            from mutagen import File
            print("✅ mutagen 已安裝")
        except ImportError:
            print("❌ mutagen 未安裝，請執行: pip install mutagen")
            return False
        
        # 匯入音樂播放器
        try:
            from music_player import create_music_player, PlaybackState
            print("✅ 音樂播放器模組載入成功")
        except ImportError as e:
            print(f"❌ 音樂播放器模組載入失敗: {e}")
            return False
        
        # 創建播放器
        print("\n🔧 創建音樂播放器...")
        try:
            player = create_music_player("downloads")
            print("✅ 播放器創建成功")
        except Exception as e:
            print(f"❌ 播放器創建失敗: {e}")
            return False
        
        # 掃描音樂資料夾
        print("\n📁 掃描音樂資料夾...")
        try:
            songs = player.scan_music_folder()
            print(f"✅ 掃描完成，找到 {len(songs)} 首歌曲")
            
            if songs:
                print("\n📋 歌曲列表:")
                for i, song in enumerate(songs[:5], 1):  # 只顯示前5首
                    print(f"  {i}. {song.title} - {song.artist} ({song.duration_str})")
                
                if len(songs) > 5:
                    print(f"  ... 還有 {len(songs) - 5} 首歌曲")
            else:
                print("ℹ️ 沒有找到音樂檔案")
                print("💡 提示: 請先在 downloads 資料夾中放入一些 MP3 檔案")
                return True  # 沒有音樂檔案不算錯誤
        
        except Exception as e:
            print(f"❌ 掃描音樂資料夾失敗: {e}")
            return False
        
        # 測試播放控制（如果有音樂檔案）
        if songs:
            print("\n🎮 測試播放控制...")
            
            # 測試播放
            try:
                print("  ▶️ 測試播放...")
                player.play(0)
                time.sleep(2)  # 播放2秒
                print("  ✅ 播放測試成功")
                
                # 測試暫停
                print("  ⏸️ 測試暫停...")
                player.pause()
                time.sleep(1)
                print("  ✅ 暫停測試成功")
                
                # 測試恢復
                print("  ▶️ 測試恢復播放...")
                player.resume()
                time.sleep(2)
                print("  ✅ 恢復播放測試成功")
                
                # 測試停止
                print("  ⏹️ 測試停止...")
                player.stop()
                print("  ✅ 停止測試成功")
                
                # 測試音量控制
                print("  🔊 測試音量控制...")
                player.set_volume(0.5)
                print("  ✅ 音量控制測試成功")
                
                # 測試播放模式
                print("  🔀 測試播放模式...")
                player.toggle_shuffle()
                player.toggle_repeat()
                print("  ✅ 播放模式測試成功")
                
            except Exception as e:
                print(f"  ❌ 播放控制測試失敗: {e}")
                return False
        
        # 測試播放器資訊
        print("\n📊 測試播放器資訊...")
        try:
            info = player.get_playlist_info()
            print(f"  ✅ 播放器資訊獲取成功")
            print(f"     - 總歌曲數: {info['total_songs']}")
            print(f"     - 播放狀態: {info['state']}")
            print(f"     - 音量: {info['volume']:.1%}")
            print(f"     - 隨機播放: {info['shuffle']}")
            print(f"     - 重複播放: {info['repeat']}")
        except Exception as e:
            print(f"  ❌ 播放器資訊測試失敗: {e}")
            return False
        
        # 清理資源
        print("\n🧹 清理資源...")
        try:
            player.cleanup()
            print("✅ 資源清理成功")
        except Exception as e:
            print(f"❌ 資源清理失敗: {e}")
        
        print("\n🎉 所有測試完成！")
        return True
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        return False

def test_iphone_background_playback():
    """測試 iPhone 背景播放功能"""
    print("\n📱 iPhone 背景播放測試")
    print("=" * 60)
    
    try:
        from music_player import create_music_player, iPhoneBackgroundPlayer
        
        # 創建播放器
        player = create_music_player("downloads")
        
        # 創建背景播放支援
        background_player = iPhoneBackgroundPlayer(player)
        
        print("✅ iPhone 背景播放支援初始化成功")
        print("ℹ️ 在實際的 iPhone 設備上，背景播放會自動啟用")
        
        # 測試背景播放控制
        background_player.enable_background_playback()
        print("✅ 背景播放啟用測試成功")
        
        background_player.disable_background_playback()
        print("✅ 背景播放停用測試成功")
        
        return True
        
    except Exception as e:
        print(f"❌ iPhone 背景播放測試失敗: {e}")
        return False

def check_music_files():
    """檢查音樂檔案"""
    print("\n📁 檢查音樂檔案")
    print("=" * 60)
    
    downloads_dir = Path("downloads")
    if not downloads_dir.exists():
        print("❌ downloads 資料夾不存在")
        return False
    
    # 尋找音樂檔案
    supported_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.m4a'}
    music_files = []
    
    for file_path in downloads_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            music_files.append(file_path)
    
    print(f"✅ 找到 {len(music_files)} 個音樂檔案")
    
    if music_files:
        print("\n📋 音樂檔案列表:")
        for i, file_path in enumerate(music_files[:10], 1):  # 只顯示前10個
            file_size = file_path.stat().st_size
            print(f"  {i}. {file_path.name} ({file_size:,} bytes)")
        
        if len(music_files) > 10:
            print(f"  ... 還有 {len(music_files) - 10} 個檔案")
    else:
        print("ℹ️ 沒有找到音樂檔案")
        print("💡 提示: 請先在 downloads 資料夾中放入一些音樂檔案")
    
    return True

def main():
    """主測試函數"""
    print("🚀 開始音樂播放器測試")
    print("=" * 60)
    
    # 檢查音樂檔案
    check_music_files()
    
    # 測試音樂播放器
    player_test_success = test_music_player()
    
    # 測試 iPhone 背景播放
    background_test_success = test_iphone_background_playback()
    
    # 總結
    print("\n" + "=" * 60)
    print("🏁 測試總結")
    print("=" * 60)
    
    if player_test_success:
        print("✅ 音樂播放器測試: 通過")
    else:
        print("❌ 音樂播放器測試: 失敗")
    
    if background_test_success:
        print("✅ iPhone 背景播放測試: 通過")
    else:
        print("❌ iPhone 背景播放測試: 失敗")
    
    if player_test_success and background_test_success:
        print("\n🎉 所有測試通過！音樂播放器功能正常")
        print("\n💡 下一步:")
        print("1. 執行 'streamlit run integrated_ui.py' 啟動整合介面")
        print("2. 或執行 'streamlit run music_player_ui.py' 啟動音樂播放器介面")
    else:
        print("\n⚠️ 部分測試失敗，請檢查錯誤訊息並安裝必要的套件")
        print("\n🔧 安裝指令:")
        print("pip install pygame mutagen")

if __name__ == "__main__":
    main() 