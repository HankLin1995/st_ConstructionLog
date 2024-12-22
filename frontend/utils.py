from re import A
import streamlit as st
import requests
import os

# 從環境變量或默認值配置 API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

def fetch_data(endpoint, project_id=None):
    """從 API 獲取數據"""
    try:
        url = f"{API_URL}/{endpoint}"
        if project_id is not None:
            url = f"{API_URL}/projects/{project_id}/{endpoint}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"獲取數據失敗：{response.text}")
            return []
    except requests.RequestException as e:
        st.error(f"獲取數據失敗：{str(e)}")
        return []

def create_data(endpoint, data):
    """創建新數據"""
    try:
        response = requests.post(
            f"{API_URL}/{endpoint}",
            json=data
        )
        if response.status_code == 200:
            st.success("創建成功！")
            return response.json()
        else:
            st.write(f"{API_URL}/{endpoint}")
            st.error(f"錯誤：{response.text}")
            return None
    except requests.RequestException as e:
        st.error(f"創建數據失敗：{str(e)}")
        return None
