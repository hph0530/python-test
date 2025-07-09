#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雲端上傳功能測試腳本
"""

import os
from pathlib import Path
from cloud_uploader import CloudUploadManager

def create_test_file():
    """建立測試檔案"""
    test_content = "這是一個測試檔案，用於驗證雲端上傳功能。\n"
    test_content += "如果您看到這個檔案，表示上傳功能正常運作！"
    
    test_file = Path("test_upload.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    return str(test_file)

def test_cloud_upload():
    """測試雲端上傳功能"""
    print("🔍 檢查雲端上傳功能...")
    
    # 建立測試檔案
    test_file = create_test_file()
    print(f"✅ 已建立測試檔案: {test_file}")
    
    # 初始化雲端上傳管理器
    try:
        cloud_manager = CloudUploadManager()
        available_services = cloud_manager.get_available_services()
        
        if not available_services:
            print("❌ 沒有可用的雲端服務")
            print("請檢查相關套件是否已安裝並正確設定")
            return
        
        print(f"✅ 找到可用的雲端服務: {', '.join(available_services)}")
        
        # 測試每個服務
        for service in available_services:
            print(f"\n🔄 測試 {service} 上傳...")
            try:
                result = cloud_manager.upload_to_service(service, test_file)
                
                if result.get('success'):
                    print(f"✅ {service} 上傳成功！")
                    print(f"   檔案名稱: {result.get('file_name')}")
                    if result.get('web_link'):
                        print(f"   分享連結: {result.get('web_link')}")
                else:
                    print(f"❌ {service} 上傳失敗: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ {service} 測試時發生錯誤: {e}")
        
        # 測試上傳到所有服務
        print(f"\n🔄 測試上傳到所有服務...")
        try:
            all_results = cloud_manager.upload_to_all_services(test_file)
            success_count = sum(1 for result in all_results.values() if result.get('success'))
            print(f"✅ 成功上傳到 {success_count}/{len(all_results)} 個服務")
            
        except Exception as e:
            print(f"❌ 批量上傳測試失敗: {e}")
    
    except Exception as e:
        print(f"❌ 初始化雲端上傳管理器失敗: {e}")
    
    finally:
        # 清理測試檔案
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"🧹 已清理測試檔案: {test_file}")

def check_config_files():
    """檢查設定檔案"""
    print("\n📋 檢查設定檔案...")
    
    config_dir = Path("cloud_config")
    if not config_dir.exists():
        print("❌ cloud_config 目錄不存在")
        return
    
    config_files = {
        "google_credentials.json": "Google Drive 認證檔案",
        "dropbox_token.txt": "Dropbox 存取權杖",
        "onedrive_config.json": "OneDrive 設定檔案"
    }
    
    for filename, description in config_files.items():
        file_path = config_dir / filename
        if file_path.exists():
            print(f"✅ {description}: {filename}")
        else:
            print(f"❌ {description}: {filename} (不存在)")

if __name__ == "__main__":
    print("🚀 開始測試雲端上傳功能")
    print("=" * 50)
    
    check_config_files()
    test_cloud_upload()
    
    print("\n" + "=" * 50)
    print("🏁 測試完成")
    print("\n💡 提示:")
    print("- 如果測試失敗，請檢查 CLOUD_SETUP.md 中的設定說明")
    print("- 確保已安裝所有必要的 Python 套件")
    print("- 檢查網路連線和雲端服務帳戶狀態") 