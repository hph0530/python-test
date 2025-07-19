#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雲端硬碟上傳模組
支援 Google Drive、OneDrive 和 Dropbox
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import json

# Google Drive
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

# Dropbox
try:
    import dropbox
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False

# OneDrive
try:
    import msal
    import requests
    ONEDRIVE_AVAILABLE = True
except ImportError:
    ONEDRIVE_AVAILABLE = False

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CloudUploader:
    """雲端硬碟上傳器基類"""
    
    def __init__(self):
        self.config_dir = Path("cloud_config")
        self.config_dir.mkdir(exist_ok=True)
    
    def upload_file(self, file_path: str, remote_path: str = None) -> Dict[str, Any]:
        """
        上傳檔案到雲端硬碟
        :param file_path: 本地檔案路徑
        :param remote_path: 遠端檔案路徑（可選）
        :return: 上傳結果字典
        """
        raise NotImplementedError("子類別必須實作此方法")

class GoogleDriveUploader(CloudUploader):
    """Google Drive 上傳器"""
    
    def __init__(self, folder_id=None):
        super().__init__()
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.credentials = None
        self.service = None
        self.folder_id = folder_id
    
    def authenticate(self) -> bool:
        """進行 Google Drive 認證"""
        try:
            creds_file = self.config_dir / "google_credentials.json"
            token_file = self.config_dir / "google_token.json"
            
            # 檢查是否有認證檔案
            if not creds_file.exists():
                logging.error("找不到 Google Drive 認證檔案。請將 google_credentials.json 放在 cloud_config 目錄中。")
                return False
            
            # 載入已存在的 token
            if token_file.exists():
                self.credentials = Credentials.from_authorized_user_file(str(token_file), self.SCOPES)
            
            # 如果沒有有效的認證，進行 OAuth 流程
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), self.SCOPES)
                    self.credentials = flow.run_local_server(port=0)
                
                # 儲存認證 token
                with open(token_file, 'w') as token:
                    token.write(self.credentials.to_json())
            
            # 建立服務
            self.service = build('drive', 'v3', credentials=self.credentials)
            return True
            
        except Exception as e:
            logging.error(f"Google Drive 認證失敗: {e}")
            return False
    
    def upload_file(self, file_path: str, remote_path: str = None, folder_id: str = None) -> Dict[str, Any]:
        """上傳檔案到 Google Drive"""
        try:
            if not self.authenticate():
                return {"success": False, "error": "認證失敗"}
            
            file_path = Path(file_path)
            if not file_path.exists():
                return {"success": False, "error": "檔案不存在"}
            
            # 設定遠端檔案名稱
            if remote_path is None:
                remote_path = file_path.name
            
            # 設定上傳目標資料夾
            target_folder_id = folder_id or self.folder_id
            file_metadata = {'name': remote_path}
            if target_folder_id:
                file_metadata['parents'] = [target_folder_id]
            media = MediaFileUpload(str(file_path), resumable=True)
            # 直接上傳新檔案到指定資料夾
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            ).execute()
            logging.info(f"已上傳到 Google Drive: {file.get('name')}")
            return {
                "success": True,
                "file_id": file.get('id'),
                "file_name": file.get('name'),
                "web_link": file.get('webViewLink'),
                "service": "Google Drive"
            }
        except Exception as e:
            logging.error(f"Google Drive 上傳失敗: {e}")
            return {"success": False, "error": str(e)}

class DropboxUploader(CloudUploader):
    """Dropbox 上傳器"""
    
    def __init__(self):
        super().__init__()
        self.dbx = None
    
    def authenticate(self, access_token: str) -> bool:
        """使用 access token 進行 Dropbox 認證"""
        try:
            self.dbx = dropbox.Dropbox(access_token)
            # 測試連線
            self.dbx.users_get_current_account()
            return True
        except Exception as e:
            logging.error(f"Dropbox 認證失敗: {e}")
            return False
    
    def upload_file(self, file_path: str, remote_path: str = None) -> Dict[str, Any]:
        """上傳檔案到 Dropbox"""
        try:
            # 從設定檔讀取 access token
            token_file = self.config_dir / "dropbox_token.txt"
            if not token_file.exists():
                return {"success": False, "error": "找不到 Dropbox access token。請在 cloud_config/dropbox_token.txt 中設定。"}
            
            with open(token_file, 'r') as f:
                access_token = f.read().strip()
            
            if not self.authenticate(access_token):
                return {"success": False, "error": "Dropbox 認證失敗"}
            
            file_path = Path(file_path)
            if not file_path.exists():
                return {"success": False, "error": "檔案不存在"}
            
            # 設定遠端檔案路徑
            if remote_path is None:
                remote_path = f"/{file_path.name}"
            elif not remote_path.startswith('/'):
                remote_path = f"/{remote_path}"
            
            # 上傳檔案
            with open(file_path, 'rb') as f:
                result = self.dbx.files_upload(f.read(), remote_path, mode=dropbox.files.WriteMode.overwrite)
            
            # 建立分享連結
            shared_link = self.dbx.sharing_create_shared_link(remote_path)
            
            logging.info(f"已上傳到 Dropbox: {result.name}")
            
            return {
                "success": True,
                "file_id": result.id,
                "file_name": result.name,
                "web_link": shared_link.url,
                "service": "Dropbox"
            }
            
        except Exception as e:
            logging.error(f"Dropbox 上傳失敗: {e}")
            return {"success": False, "error": str(e)}

class OneDriveUploader(CloudUploader):
    """OneDrive 上傳器"""
    
    def __init__(self):
        super().__init__()
        self.access_token = None
        self.app = None
    
    def authenticate(self, client_id: str, client_secret: str, tenant_id: str) -> bool:
        """進行 OneDrive 認證"""
        try:
            authority = f"https://login.microsoftonline.com/{tenant_id}"
            self.app = msal.ConfidentialClientApplication(
                client_id,
                authority=authority,
                client_credential=client_secret
            )
            
            # 使用 client credentials flow
            result = self.app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                return True
            else:
                logging.error(f"OneDrive 認證失敗: {result.get('error_description', '未知錯誤')}")
                return False
                
        except Exception as e:
            logging.error(f"OneDrive 認證失敗: {e}")
            return False
    
    def upload_file(self, file_path: str, remote_path: str = None) -> Dict[str, Any]:
        """上傳檔案到 OneDrive"""
        try:
            # 從設定檔讀取認證資訊
            config_file = self.config_dir / "onedrive_config.json"
            if not config_file.exists():
                return {"success": False, "error": "找不到 OneDrive 設定檔。請在 cloud_config/onedrive_config.json 中設定。"}
            
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            if not self.authenticate(config['client_id'], config['client_secret'], config['tenant_id']):
                return {"success": False, "error": "OneDrive 認證失敗"}
            
            file_path = Path(file_path)
            if not file_path.exists():
                return {"success": False, "error": "檔案不存在"}
            
            # 設定遠端檔案路徑
            if remote_path is None:
                remote_path = file_path.name
            
            # 上傳檔案到 OneDrive
            upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{remote_path}:/content"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/octet-stream'
            }
            
            with open(file_path, 'rb') as f:
                response = requests.put(upload_url, headers=headers, data=f)
            
            if response.status_code == 200 or response.status_code == 201:
                file_info = response.json()
                
                # 建立分享連結
                share_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_info['id']}/createLink"
                share_data = {
                    "type": "view",
                    "scope": "anonymous"
                }
                
                share_response = requests.post(share_url, headers=headers, json=share_data)
                if share_response.status_code == 200:
                    share_info = share_response.json()
                    web_link = share_info['link']['webUrl']
                else:
                    web_link = None
                
                logging.info(f"已上傳到 OneDrive: {file_info['name']}")
                
                return {
                    "success": True,
                    "file_id": file_info['id'],
                    "file_name": file_info['name'],
                    "web_link": web_link,
                    "service": "OneDrive"
                }
            else:
                return {"success": False, "error": f"上傳失敗: {response.status_code} - {response.text}"}
                
        except Exception as e:
            logging.error(f"OneDrive 上傳失敗: {e}")
            return {"success": False, "error": str(e)}

class CloudUploadManager:
    """雲端硬碟上傳管理器"""
    
    def __init__(self, folder_id=None):
        self.uploader = GoogleDriveUploader(folder_id=folder_id)
    
    def get_available_services(self) -> list:
        """獲取可用的雲端服務列表"""
        services = []
        
        # 檢查 Google Drive
        if GOOGLE_AVAILABLE:
            creds_file = Path("cloud_config") / "google_credentials.json"
            if creds_file.exists():
                services.append("google_drive")
        
        # 檢查 Dropbox
        if DROPBOX_AVAILABLE:
            token_file = Path("cloud_config") / "dropbox_token.txt"
            if token_file.exists():
                services.append("dropbox")
        
        # 檢查 OneDrive
        if ONEDRIVE_AVAILABLE:
            config_file = Path("cloud_config") / "onedrive_config.json"
            if config_file.exists():
                services.append("onedrive")
        
        return services
    
    def upload_to_service(self, service: str, file_path: str, remote_path: str = None) -> Dict[str, Any]:
        """上傳檔案到指定的雲端服務"""
        try:
            if service == "google_drive":
                return self.uploader.upload_file(file_path, remote_path)
            elif service == "dropbox":
                dropbox_uploader = DropboxUploader()
                return dropbox_uploader.upload_file(file_path, remote_path)
            elif service == "onedrive":
                onedrive_uploader = OneDriveUploader()
                return onedrive_uploader.upload_file(file_path, remote_path)
            else:
                return {"success": False, "error": f"不支援的服務: {service}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def upload_to_all_services(self, file_path: str, remote_path: str = None) -> Dict[str, Dict[str, Any]]:
        """上傳檔案到所有可用的雲端服務"""
        results = {}
        available_services = self.get_available_services()
        
        for service in available_services:
            results[service] = self.upload_to_service(service, file_path, remote_path)
        
        return results
    
    def upload(self, file_path: str, remote_path: str = None) -> Dict[str, Any]:
        """預設上傳到 Google Drive"""
        return self.uploader.upload_file(file_path, remote_path) 