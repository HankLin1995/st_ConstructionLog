import streamlit as st
from utils import fetch_data, create_data

st.header("工程專案管理")

# 創建新專案表單
with st.expander("新增工程專案"):
    with st.form("project_form"):
        name = st.text_input("專案名稱")
        contract_number = st.text_input("合約編號")
        contractor = st.text_input("施工廠商")
        location= st.text_input("工程地點")

        submitted = st.form_submit_button("創建專案")
        
        if submitted:
            data={
                "name": name,
                "contract_number": contract_number,
                "contractor": contractor,
                "location": location
            }

            create_data("projects", data)

# 顯示現有專案
projects = fetch_data("projects")
if projects:
    for project in projects:
        with st.expander(f"{project['name']} ({project['contract_number']})"):
            pass
