#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
密碼驗證模組
用於保護程式存取，只有輸入正確密碼才能使用功能
"""

import streamlit as st
import hashlib
import time

# 預設密碼 (2681815)
DEFAULT_PASSWORD = "2681815"

def hash_password(password):
    """對密碼進行雜湊處理"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(input_password, stored_password_hash):
    """驗證密碼"""
    return hash_password(input_password) == stored_password_hash

def init_password_session():
    """初始化密碼相關的 session state"""
    if 'password_verified' not in st.session_state:
        st.session_state.password_verified = False
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    if 'lockout_time' not in st.session_state:
        st.session_state.lockout_time = 0
    if 'stored_password_hash' not in st.session_state:
        # 預設密碼的雜湊值
        st.session_state.stored_password_hash = hash_password(DEFAULT_PASSWORD)

def check_lockout():
    """檢查是否被鎖定"""
    if st.session_state.login_attempts >= 5:
        lockout_duration = 300  # 5分鐘鎖定
        if time.time() - st.session_state.lockout_time < lockout_duration:
            remaining_time = int(lockout_duration - (time.time() - st.session_state.lockout_time))
            return True, remaining_time
        else:
            # 鎖定時間結束，重置
            st.session_state.login_attempts = 0
            st.session_state.lockout_time = 0
    return False, 0

def show_login_page():
    """顯示登入頁面"""
    st.set_page_config(
        page_title="🔐 密碼驗證",
        page_icon="🔐",
        layout="centered"
    )
    
    # 初始化 session state
    init_password_session()
    
    # 檢查鎖定狀態
    is_locked, remaining_time = check_lockout()
    
    if is_locked:
        st.error(f"🔒 帳戶已被鎖定，請等待 {remaining_time} 秒後再試")
        st.info("💡 提示：連續輸入錯誤密碼 5 次會導致帳戶鎖定 5 分鐘")
        return False
    
    # 登入介面
    st.title("🔐 密碼驗證")
    st.markdown("請輸入密碼以存取程式功能")
    
    # 密碼輸入
    password = st.text_input("密碼", type="password", placeholder="請輸入密碼")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔓 登入", type="primary", use_container_width=True):
            if password:
                if verify_password(password, st.session_state.stored_password_hash):
                    st.session_state.password_verified = True
                    st.session_state.login_attempts = 0
                    st.success("✅ 密碼正確！正在進入程式...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    if st.session_state.login_attempts >= 5:
                        st.session_state.lockout_time = time.time()
                        st.error("🔒 密碼錯誤次數過多，帳戶已被鎖定 5 分鐘")
                    else:
                        remaining_attempts = 5 - st.session_state.login_attempts
                        st.error(f"❌ 密碼錯誤！還剩 {remaining_attempts} 次嘗試機會")
            else:
                st.warning("⚠️ 請輸入密碼")
    
    with col2:
        if st.button("🔄 重置", use_container_width=True):
            st.session_state.login_attempts = 0
            st.session_state.lockout_time = 0
            st.success("✅ 已重置登入狀態")
            st.rerun()
    
    # 顯示嘗試次數
    if st.session_state.login_attempts > 0:
        st.info(f"📊 登入嘗試次數: {st.session_state.login_attempts}/5")
    
    # 密碼提示
    st.markdown("---")
    st.info("💡 **密碼提示**: 請聯繫管理員獲取密碼")
    
    # 安全提示
    st.markdown("---")
    st.warning("⚠️ **安全提醒**:")
    st.markdown("""
    - 請勿在公共場所輸入密碼
    - 請勿與他人分享密碼
    - 定期更換密碼以確保安全
    - 如忘記密碼，請聯繫管理員
    """)
    
    return False

def require_password(func):
    """裝飾器：要求密碼驗證"""
    def wrapper(*args, **kwargs):
        init_password_session()
        
        if not st.session_state.password_verified:
            return show_login_page()
        
        return func(*args, **kwargs)
    
    return wrapper

def change_password():
    """更改密碼功能"""
    st.subheader("🔐 更改密碼")
    
    current_password = st.text_input("當前密碼", type="password")
    new_password = st.text_input("新密碼", type="password")
    confirm_password = st.text_input("確認新密碼", type="password")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("✅ 確認更改", type="primary", use_container_width=True):
            if not current_password or not new_password or not confirm_password:
                st.warning("⚠️ 請填寫所有欄位")
                return
            
            if not verify_password(current_password, st.session_state.stored_password_hash):
                st.error("❌ 當前密碼錯誤")
                return
            
            if new_password != confirm_password:
                st.error("❌ 新密碼與確認密碼不符")
                return
            
            if len(new_password) < 6:
                st.error("❌ 新密碼長度至少需要 6 個字元")
                return
            
            # 更新密碼
            st.session_state.stored_password_hash = hash_password(new_password)
            st.success("✅ 密碼更改成功！")
            st.info("請重新登入以使用新密碼")
            st.session_state.password_verified = False
            time.sleep(2)
            st.rerun()
    
    with col2:
        if st.button("❌ 取消", use_container_width=True):
            st.rerun()

def logout():
    """登出功能"""
    st.session_state.password_verified = False
    st.session_state.login_attempts = 0
    st.session_state.lockout_time = 0
    st.success("✅ 已成功登出")
    time.sleep(1)
    st.rerun()

def show_security_info():
    """顯示安全資訊"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔐 安全資訊")
    
    # 登入狀態
    if st.session_state.password_verified:
        st.sidebar.success("✅ 已登入")
        if st.sidebar.button("🚪 登出", use_container_width=True):
            logout()
    else:
        st.sidebar.error("❌ 未登入")
    
    # 嘗試次數
    if st.session_state.login_attempts > 0:
        st.sidebar.info(f"📊 嘗試次數: {st.session_state.login_attempts}/5")
    
    # 鎖定狀態
    is_locked, remaining_time = check_lockout()
    if is_locked:
        st.sidebar.warning(f"🔒 鎖定中: {remaining_time}s")
    
    # 密碼管理
    st.sidebar.markdown("---")
    if st.sidebar.button("🔐 更改密碼", use_container_width=True):
        st.session_state.show_change_password = True
    
    if st.sidebar.button("ℹ️ 安全說明", use_container_width=True):
        st.session_state.show_security_help = True

def show_security_help():
    """顯示安全說明"""
    st.subheader("ℹ️ 安全說明")
    
    st.markdown("""
    ### 🔐 密碼安全
    
    **密碼要求**:
    - 長度至少 6 個字元
    - 建議使用字母、數字和符號組合
    - 避免使用常見密碼
    
    **安全措施**:
    - 連續錯誤 5 次會鎖定帳戶 5 分鐘
    - 密碼使用 SHA-256 雜湊加密
    - 登入狀態會保持到登出或重新整理
    
    **使用建議**:
    - 定期更換密碼
    - 不要在公共場所輸入密碼
    - 不要與他人分享密碼
    - 使用完畢後記得登出
    
    ### 🛡️ 技術細節
    
    **加密方式**: SHA-256 雜湊
    **鎖定機制**: 5 次錯誤後鎖定 5 分鐘
    **會話管理**: Streamlit Session State
    **安全等級**: 中等安全級別
    """)
    
    if st.button("✅ 了解", type="primary"):
        st.session_state.show_security_help = False
        st.rerun() 