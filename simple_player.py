#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單命令列音樂播放器
用於測試音訊播放功能
"""

import time
import threading
from pathlib import Path

def test_audio_playback():
    """測試音訊播放功能"""
    print("🎵 簡單音訊播放器測試")
    print("=" * 50)
    
    try:
        from music_player import create_music_player
        
        # 創建播放器
        player = create_music_player("downloads")
        
        # 掃描音樂檔案
        songs = player.scan_music_folder()
        
        if not songs:
            print("❌ 沒有找到音樂檔案")
            return
        
        print(f"✅ 找到 {len(songs)} 首歌曲")
        
        # 顯示前5首歌曲
        print("\n📋 可播放的歌曲:")
        for i, song in enumerate(songs[:5], 1):
            print(f"  {i}. {song.title} ({song.duration_str})")
        
        # 選擇歌曲播放
        try:
            choice = int(input(f"\n請選擇要播放的歌曲 (1-{min(5, len(songs))}): "))
            if 1 <= choice <= min(5, len(songs)):
                selected_song = songs[choice - 1]
                print(f"\n🎵 開始播放: {selected_song.title}")
                
                # 設定音量
                player.set_volume(0.8)
                print("🔊 音量設定為 80%")
                
                # 開始播放
                player.play(choice - 1)
                
                # 播放控制選單
                while True:
                    print("\n🎮 播放控制:")
                    print("  1. 暫停/恢復")
                    print("  2. 停止")
                    print("  3. 下一首")
                    print("  4. 上一首")
                    print("  5. 調整音量")
                    print("  6. 退出")
                    
                    control = input("請選擇操作 (1-6): ")
                    
                    if control == "1":
                        if player.state.value == "playing":
                            player.pause()
                            print("⏸️ 已暫停")
                        else:
                            player.resume()
                            print("▶️ 已恢復播放")
                    
                    elif control == "2":
                        player.stop()
                        print("⏹️ 已停止")
                        break
                    
                    elif control == "3":
                        player.next()
                        print("⏭️ 下一首")
                    
                    elif control == "4":
                        player.previous()
                        print("⏮️ 上一首")
                    
                    elif control == "5":
                        try:
                            vol = float(input("請輸入音量 (0.0-1.0): "))
                            player.set_volume(vol)
                            print(f"🔊 音量已調整為 {vol:.1%}")
                        except ValueError:
                            print("❌ 無效的音量值")
                    
                    elif control == "6":
                        player.stop()
                        print("👋 再見！")
                        break
                    
                    else:
                        print("❌ 無效的選擇")
                
            else:
                print("❌ 無效的選擇")
        
        except ValueError:
            print("❌ 請輸入有效的數字")
        
        # 清理資源
        player.cleanup()
        
    except Exception as e:
        print(f"❌ 播放器測試失敗: {e}")

def test_single_file():
    """測試單一檔案播放"""
    print("\n🎵 單一檔案播放測試")
    print("=" * 50)
    
    try:
        import pygame
        
        # 尋找第一個 MP3 檔案
        downloads_dir = Path("downloads")
        mp3_files = list(downloads_dir.glob("*.mp3"))
        
        if not mp3_files:
            print("❌ 沒有找到 MP3 檔案")
            return
        
        test_file = mp3_files[0]
        print(f"🎵 測試播放: {test_file.name}")
        
        # 初始化 pygame
        pygame.mixer.init()
        
        # 載入並播放
        pygame.mixer.music.load(str(test_file))
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play()
        
        print("▶️ 開始播放...")
        print("⏸️ 按 Enter 暫停/恢復，輸入 'q' 退出")
        
        paused = False
        while True:
            user_input = input()
            
            if user_input.lower() == 'q':
                break
            elif user_input == '':
                if paused:
                    pygame.mixer.music.unpause()
                    paused = False
                    print("▶️ 恢復播放")
                else:
                    pygame.mixer.music.pause()
                    paused = True
                    print("⏸️ 已暫停")
        
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        print("👋 播放結束")
        
    except Exception as e:
        print(f"❌ 單一檔案播放測試失敗: {e}")

def main():
    """主函數"""
    print("🚀 音訊播放測試")
    print("=" * 60)
    
    print("請選擇測試模式:")
    print("1. 完整播放器測試")
    print("2. 單一檔案播放測試")
    
    try:
        choice = input("請選擇 (1-2): ")
        
        if choice == "1":
            test_audio_playback()
        elif choice == "2":
            test_single_file()
        else:
            print("❌ 無效的選擇")
    
    except KeyboardInterrupt:
        print("\n👋 測試已取消")
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    main() 