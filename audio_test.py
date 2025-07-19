#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音訊播放測試腳本
測試系統音訊播放功能
"""

import time
import pygame
from pathlib import Path

def test_system_audio():
    """測試系統音訊播放"""
    print("🔊 系統音訊測試")
    print("=" * 50)
    
    try:
        # 初始化 pygame
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        print("✅ Pygame 音訊系統初始化成功")
        
        # 尋找測試檔案
        downloads_dir = Path("downloads")
        mp3_files = list(downloads_dir.glob("*.mp3"))
        
        if not mp3_files:
            print("❌ 沒有找到 MP3 檔案進行測試")
            return False
        
        test_file = mp3_files[0]
        print(f"🎵 測試檔案: {test_file.name}")
        
        # 載入音訊檔案
        try:
            pygame.mixer.music.load(str(test_file))
            print("✅ 音訊檔案載入成功")
        except Exception as e:
            print(f"❌ 音訊檔案載入失敗: {e}")
            return False
        
        # 設定音量
        pygame.mixer.music.set_volume(0.8)
        print("🔊 音量設定為 80%")
        
        # 開始播放
        print("▶️ 開始播放...")
        print("⏸️ 按 Enter 暫停/恢復，輸入 'q' 退出")
        
        pygame.mixer.music.play()
        
        paused = False
        while True:
            try:
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
                
            except KeyboardInterrupt:
                break
        
        # 停止播放
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        print("👋 播放結束")
        return True
        
    except Exception as e:
        print(f"❌ 音訊測試失敗: {e}")
        return False

def check_audio_devices():
    """檢查音訊裝置"""
    print("\n🔍 音訊裝置檢查")
    print("=" * 50)
    
    try:
        # 嘗試獲取音訊驅動程式資訊
        pygame.mixer.init()
        print("✅ 音訊驅動程式初始化成功")
        
        # 獲取音訊驅動程式資訊
        driver_info = pygame.mixer.get_init()
        if driver_info:
            print(f"✅ 音訊驅動程式: {driver_info}")
        
        pygame.mixer.quit()
        
    except Exception as e:
        print(f"❌ 音訊驅動程式檢查失敗: {e}")

def main():
    """主函數"""
    print("🚀 音訊播放功能測試")
    print("=" * 60)
    
    # 檢查音訊裝置
    check_audio_devices()
    
    # 測試音訊播放
    success = test_system_audio()
    
    print("\n" + "=" * 60)
    print("🏁 測試總結")
    print("=" * 60)
    
    if success:
        print("✅ 音訊播放測試: 成功")
        print("\n💡 如果網頁播放器沒有聲音，請嘗試:")
        print("1. 檢查瀏覽器音訊設定")
        print("2. 使用 'streamlit run web_audio_player.py'")
        print("3. 確保瀏覽器允許音訊播放")
    else:
        print("❌ 音訊播放測試: 失敗")
        print("\n🔧 請檢查:")
        print("1. 系統音訊設定")
        print("2. 音訊驅動程式")
        print("3. 音訊輸出裝置")

if __name__ == "__main__":
    main() 