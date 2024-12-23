import streamlit as st
import utils
import pandas as pd
import os
import time

API_URL = os.getenv("API_URL", "http://localhost:8000")

@st.dialog("新增工程專案")
def create_project_UI():
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
            utils.create_data("projects", data)

            st.toast("專案建立成功！")
            time.sleep(1)
            st.rerun()
            

@st.dialog("編輯工程專案")
def edit_project_UI(project): ## 傳入物件
    with st.form("edit_project_form"):
        name = st.text_input("專案名稱", value=project["name"])
        contract_number = st.text_input("合約編號", value=project["contract_number"])
        contractor = st.text_input("施工廠商", value=project["contractor"])
        location = st.text_input("工程地點", value=project["location"])

        submitted = st.form_submit_button("更新專案")
        
        if submitted:
            data = {
                "name": name,
                "contract_number": contract_number,
                "contractor": contractor,
                "location": location
            }
            if utils.update_data("projects",st.session_state["project_id"], data):
                st.toast("專案更新成功！")
                time.sleep(1)
                st.rerun()

if st.sidebar.button("新增專案"):
    create_project_UI()

if st.sidebar.button("編輯專案"):
    edit_project_UI(utils.fetch_data_by_id("projects", st.session_state["project_id"]))

if st.sidebar.button("刪除專案"):
    utils.delete_data("projects",st.session_state["project_id"])

## 顯示現有工程專案

projects = utils.fetch_data("projects")

project_df = pd.DataFrame(projects)
project_df = project_df[['id','name', 'contract_number', 'contractor', 'location', 'created_at', 'updated_at']]
project_df.columns = ['ID','專案名稱', '合約編號', '施工廠商', '工程地點', '新增日期', '更新日期']

event=st.dataframe(project_df,
                    hide_index=True,
                    use_container_width=True,
                    on_select="rerun",
                    selection_mode="multi-row"
)

# 檢查是否有選擇專案
if event :
    project = event.selection.rows  # 選擇的行索引列表

    if len(project)!=0:

        selected_project_id = project_df.iloc[project[0]]["ID"]
        st.session_state["project_id"] = selected_project_id
        st.toast(f"目前專案已經預設為 {project_df.iloc[project[0]]['專案名稱']}")

else:
    st.session_state["project_id"] = None






    
