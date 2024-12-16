# 2023-12-16: 創建了 Streamlit 前端界面
# 1. 實現了與 FastAPI 後端的完整集成
# 2. 添加了項目、合同項目和質量測試的管理界面
# 3. 實現了基於項目的數據過濾和關聯顯示

import streamlit as st
import requests
import json
import os
from datetime import datetime

# 從環境變量或默認值配置 API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

# 設置頁面配置
st.set_page_config(
    page_title="Quality Management System",
    page_icon="🏭",
    layout="wide"
)

# 標題和描述
st.title("Quality Management System")
st.markdown("Manage your projects, contracts, and quality tests in one place.")

# 側邊欄導航
page = st.sidebar.selectbox(
    "Select Page",
    ["Projects", "Contract Items", "Quality Tests"]
)

def fetch_data(endpoint, project_id=None):
    """
    從 API 獲取數據
    
    Args:
        endpoint (str): API 端點
        project_id (int, optional): 項目 ID，用於過濾特定項目的數據
    
    Returns:
        list: API 返回的數據列表
    """
    try:
        url = f"{API_URL}/{endpoint}"
        if project_id is not None:
            url = f"{API_URL}/projects/{project_id}/{endpoint}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching data: {response.text}")
            return []
    except requests.RequestException as e:
        st.error(f"Error fetching data: {str(e)}")
        return []

def create_data(endpoint, data):
    """
    創建新數據
    
    Args:
        endpoint (str): API 端點
        data (dict): 要創建的數據
    
    Returns:
        dict: 創建成功返回的數據，失敗返回 None
    """
    try:
        response = requests.post(
            f"{API_URL}/{endpoint}",
            json=data
        )
        if response.status_code == 200:
            st.success("Created successfully!")
            return response.json()
        else:
            st.error(f"Error: {response.text}")
            return None
    except requests.RequestException as e:
        st.error(f"Error creating data: {str(e)}")
        return None

# 項目管理頁面
if page == "Projects":
    st.header("Projects Management")
    
    # 創建新項目表單
    with st.expander("Create New Project"):
        with st.form("new_project"):
            project_name = st.text_input("Project Name")
            contract_number = st.text_input("Contract Number")
            contractor = st.text_input("Contractor")
            location = st.text_input("Location")
            submit = st.form_submit_button("Create Project")
            
            if submit and project_name and contract_number and contractor and location:
                create_data("projects", {
                    "name": project_name,
                    "contract_number": contract_number,
                    "contractor": contractor,
                    "location": location
                })
    
    # 顯示現有項目
    st.subheader("Existing Projects")
    projects = fetch_data("projects")
    for project in projects:
        with st.expander(f"Project: {project.get('name', 'Unnamed Project')}"):
            st.write(f"ID: {project.get('id', 'N/A')}")
            st.write(f"Contract Number: {project.get('contract_number', 'N/A')}")
            st.write(f"Contractor: {project.get('contractor', 'N/A')}")
            st.write(f"Location: {project.get('location', 'N/A')}")
            st.write(f"Created at: {project.get('created_at', 'N/A')}")

# 合同項目管理頁面
elif page == "Contract Items":
    st.header("Contract Items Management")
    
    # 創建新合同項目表單
    with st.expander("Create New Contract Item"):
        projects = fetch_data("projects")
        project_choices = {p.get('name', 'Unnamed'): p.get('id') 
                         for p in projects if p.get('id')}
        
        with st.form("new_contract_item"):
            project = st.selectbox("Select Project", list(project_choices.keys()))
            pcces_code = st.text_input("PCCES Code")
            item_name = st.text_input("Item Name")
            unit = st.text_input("Unit")
            quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
            unit_price = st.number_input("Unit Price", min_value=0.0, step=0.1)
            total_price = st.number_input("Total Price", min_value=0.0, step=0.1)
            submit = st.form_submit_button("Create Contract Item")
            
            if submit and all([project, pcces_code, item_name, unit]):
                create_data("contract-items", {
                    "project_id": project_choices[project],
                    "pcces_code": pcces_code,
                    "name": item_name,
                    "unit": unit,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": total_price
                })
    
    # 選擇項目以查看其合同項目
    selected_project = st.selectbox(
        "Select Project to View Contract Items",
        list(project_choices.keys())
    )
    
    # 顯示選定項目的合同項目
    if selected_project:
        st.subheader(f"Contract Items for {selected_project}")
        contract_items = fetch_data("contract-items", project_choices[selected_project])
        for item in contract_items:
            with st.expander(f"Contract Item: {item.get('name', 'Unnamed Item')}"):
                st.write(f"ID: {item.get('id', 'N/A')}")
                st.write(f"PCCES Code: {item.get('pcces_code', 'N/A')}")
                st.write(f"Unit: {item.get('unit', 'N/A')}")
                st.write(f"Quantity: {item.get('quantity', 'N/A')}")
                st.write(f"Unit Price: {item.get('unit_price', 'N/A')}")
                st.write(f"Total Price: {item.get('total_price', 'N/A')}")

# 質量測試管理頁面
elif page == "Quality Tests":
    st.header("Quality Tests Management")
    
    # 創建新質量測試表單
    with st.expander("Create New Quality Test"):
        projects = fetch_data("projects")
        project_choices = {p.get('name', 'Unnamed'): p.get('id') 
                         for p in projects if p.get('id')}
        
        with st.form("new_quality_test"):
            project = st.selectbox("Select Project", list(project_choices.keys()))
            
            # 根據選擇的項目加載相關的合同項目
            if project:
                contract_items = fetch_data("contract-items", project_choices[project])
                item_choices = {
                    f"{item.get('pcces_code', 'N/A')} - {item.get('name', 'Unnamed')}": item.get('id')
                    for item in contract_items if item.get('id')
                }
                
                contract_item = st.selectbox("Select Contract Item", list(item_choices.keys()))
                name = st.text_input("Test Name")
                test_item = st.text_input("Test Item")
                test_sets = st.number_input("Test Sets", min_value=1, step=1)
                test_result = st.selectbox("Test Result", ["PASS", "FAIL", "PENDING"])
                submit = st.form_submit_button("Create Quality Test")
                
                if submit and all([project, contract_item, name, test_item]):
                    create_data("tests", {
                        "project_id": project_choices[project],
                        "contract_item_id": item_choices[contract_item],
                        "name": name,
                        "test_item": test_item,
                        "test_sets": test_sets,
                        "test_result": test_result
                    })
    
    # 選擇項目以查看其質量測試
    selected_project = st.selectbox(
        "Select Project to View Quality Tests",
        list(project_choices.keys())
    )
    
    # 顯示選定項目的質量測試
    if selected_project:
        st.subheader(f"Quality Tests for {selected_project}")
        quality_tests = fetch_data("tests", project_choices[selected_project])
        for test in quality_tests:
            with st.expander(f"Test: {test.get('name', 'Unnamed Test')}"):
                st.write(f"ID: {test.get('id', 'N/A')}")
                st.write(f"Contract Item ID: {test.get('contract_item_id', 'N/A')}")
                st.write(f"Test Item: {test.get('test_item', 'N/A')}")
                st.write(f"Test Sets: {test.get('test_sets', 'N/A')}")
                st.write(f"Result: {test.get('test_result', 'N/A')}")

# 添加頁腳
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ using Streamlit and FastAPI")
