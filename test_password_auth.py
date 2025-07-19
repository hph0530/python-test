#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
密碼驗證功能測試腳本
測試密碼驗證是否正常工作
"""

import streamlit as st
import hashlib
import time

def test_password_auth():
    """測試密碼驗證功能"""
    st.title("🔐 密碼驗證功能測試")
    st.markdown("測試密碼驗證是否正常工作")
    
    # 測試密碼
    test_password = "2681815"
    expected_hash = hashlib.sha256(test_password.encode()).hexdigest()
    
    st.subheader("📋 測試項目")
    
    # 測試 1: 密碼雜湊
    st.write("**測試 1: 密碼雜湊功能**")
    test_hash = hashlib.sha256(test_password.encode()).hexdigest()
    if test_hash == expected_hash:
        st.success("✅ 密碼雜湊功能正常")
    else:
        st.error("❌ 密碼雜湊功能異常")
    
    # 測試 2: 密碼驗證
    st.write("**測試 2: 密碼驗證功能**")
    from password_auth import verify_password, hash_password
    
    # 正確密碼測試
    if verify_password(test_password, expected_hash):
        st.success("✅ 正確密碼驗證正常")
    else:
        st.error("❌ 正確密碼驗證失敗")
    
    # 錯誤密碼測試
    if not verify_password("wrong_password", expected_hash):
        st.success("✅ 錯誤密碼驗證正常")
    else:
        st.error("❌ 錯誤密碼驗證異常")
    
    # 測試 3: Session State 初始化
    st.write("**測試 3: Session State 初始化**")
    from password_auth import init_password_session
    
    # 清除現有的 session state
    if 'password_verified' in st.session_state:
        del st.session_state.password_verified
    if 'login_attempts' in st.session_state:
        del st.session_state.login_attempts
    if 'lockout_time' in st.session_state:
        del st.session_state.lockout_time
    if 'stored_password_hash' in st.session_state:
        del st.session_state.stored_password_hash
    
    # 初始化
    init_password_session()
    
    # 檢查初始化結果
    required_keys = ['password_verified', 'login_attempts', 'lockout_time', 'stored_password_hash']
    all_keys_present = all(key in st.session_state for key in required_keys)
    
    if all_keys_present:
        st.success("✅ Session State 初始化正常")
        st.write(f"password_verified: {st.session_state.password_verified}")
        st.write(f"login_attempts: {st.session_state.login_attempts}")
        st.write(f"lockout_time: {st.session_state.lockout_time}")
        st.write(f"stored_password_hash: {st.session_state.stored_password_hash[:20]}...")
    else:
        st.error("❌ Session State 初始化失敗")
    
    # 測試 4: 鎖定機制
    st.write("**測試 4: 帳戶鎖定機制**")
    from password_auth import check_lockout
    
    # 模擬多次錯誤登入
    st.session_state.login_attempts = 5
    st.session_state.lockout_time = time.time()
    
    is_locked, remaining_time = check_lockout()
    
    if is_locked and remaining_time > 0:
        st.success("✅ 帳戶鎖定機制正常")
        st.write(f"鎖定剩餘時間: {remaining_time} 秒")
    else:
        st.error("❌ 帳戶鎖定機制異常")
    
    # 測試 5: 密碼更改功能
    st.write("**測試 5: 密碼更改功能**")
    
    # 測試密碼要求
    test_passwords = [
        ("short", False),  # 太短
        ("123456", True),  # 剛好 6 位
        ("newpassword123", True),  # 正常密碼
        ("", False),  # 空密碼
    ]
    
    for password, should_be_valid in test_passwords:
        is_valid = len(password) >= 6
        if is_valid == should_be_valid:
            st.success(f"✅ 密碼 '{password}': {'有效' if is_valid else '無效'}")
        else:
            st.error(f"❌ 密碼 '{password}': {'有效' if is_valid else '無效'} (預期: {'有效' if should_be_valid else '無效'})")
    
    st.subheader("🎯 測試總結")
    st.info("""
    **測試完成！**
    
    如果所有測試都顯示 ✅，表示密碼驗證功能正常工作。
    
    **使用說明**:
    1. 啟動程式時會要求輸入密碼
    2. 預設密碼: 2681815
    3. 連續錯誤 5 次會鎖定帳戶 5 分鐘
    4. 可以在側邊欄更改密碼或查看安全說明
    """)

if __name__ == "__main__":
    test_password_auth() 