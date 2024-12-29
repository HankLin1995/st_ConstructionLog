import streamlit as st
import requests
from datetime import datetime
import os
from pathlib import Path
import tempfile
import pandas as pd
import utils

@st.dialog("新增抽查表")
def create_inspection_UI():
        
    with st.form("inspection_form"):
        name = st.text_input("抽查表名稱")
        inspection_time = st.date_input("抽查日期", value=datetime.now())
        location = st.text_input("抽查地點")
        is_pass = st.selectbox("是否合格", options=["是", "否"])
        is_pass_bool = is_pass == "是"
        uploaded_file = st.file_uploader("上傳抽查表PDF", type=["pdf"])

        submitted = st.form_submit_button("提交")

        if submitted and uploaded_file is not None:

            data={
                "name": name,
                "inspection_time": f"{inspection_time}T00:00:00",
                "location": location,
                "is_pass": is_pass_bool,
                "file_path": "",
                "project_id": st.session_state.project_id
            }

            response = utils.create_data("inspections", data)

            if response:
                inspection_id = response["id"]

                # 創建臨時文件來保存上傳的PDF
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name

                # 上傳PDF文件
                files = {"file": ("inspection.pdf", open(tmp_file_path, "rb"), "application/pdf")}
                data={
                    "project_id": st.session_state.project_id,
                    "inspection_id": inspection_id
                }
                upload_response = utils.upload_file(
                    "upload-inspection-file",
                    files,
                    data
                )

                if upload_response:
                    st.success("抽查表上傳成功！")
                else:
                    st.error("文件上傳失敗")

                # 清理臨時文件
                os.unlink(tmp_file_path)



project_id = st.session_state.project_id

if project_id is None:
    project_list=utils.fetch_data("projects", project_id=None)
    if project_list:
        project_names = {f"{p['name']} ({p['contract_number']})": p['id'] for p in project_list}
        selected_project = st.sidebar.selectbox("選擇工程專案", options=list(project_names.keys()))
        project_id = project_names[selected_project]
        st.session_state.project_id = project_id

# 抽查表清單

inspections = utils.fetch_data("inspections", project_id)

df= pd.DataFrame(inspections)

df_show=df[['name','inspection_time','location','updated_at']]
df_show.columns=['抽查表名稱','抽查日期','抽查地點','更新日期']

if inspections:
    st.subheader("抽查表清單")
    st.dataframe(df_show,hide_index=True,use_container_width=True)
else:
    st.info("尚無抽查表")

# 新增抽查表

st.markdown("---")

if st.button("新增抽查表"):
    create_inspection_UI()




    # if submit_button and uploaded_file is not None:
    #     # 創建臨時文件來保存上傳的PDF
    #     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
    #         tmp_file.write(uploaded_file.getvalue())
    #         tmp_file_path = tmp_file.name

    #     # 創建抽查記錄
    #     inspection_data = {
    #         "name": name,
    #         "inspection_time": f"{inspection_time}T00:00:00",
    #         "location": location,
    #         "is_pass": is_pass,
    #         "file_path": "",  # 先創建記錄，稍後更新文件路徑
    #         "project_id": project_id
    #     }

    #     response = utils.create_data("inspections", inspection_data)
    #     if response:
    #         inspection_id = response["id"]

    #         # 上傳PDF文件
    #         files = {"file": ("inspection.pdf", open(tmp_file_path, "rb"), "application/pdf")}
    #         upload_response = utils.upload_file(
    #             f"{utils.API_URL}/inspections/upload",
    #             files,
    #             data={"project_id": project_id, "inspection_id": inspection_id}
    #         )

    #         if upload_response:
    #             st.success("抽查表上傳成功！")
    #         else:
    #             st.error("文件上傳失敗")

    #         # 清理臨時文件
    #         os.unlink(tmp_file_path)
    #     else:
    #         st.error("創建抽查記錄失敗")


    # st.sidebar.subheader("目前專案")
    # st.sidebar.write(project_name)



# def upload_inspection():
#     st.title("施工抽查表管理")
    
#     # 選擇工程專案
#     projects = utils.fetch_data("projects", project_id=None)
#     if projects:
#         project_names = {f"{p['name']} ({p['contract_number']})": p['id'] for p in projects}
#         selected_project = st.selectbox("選擇工程專案", options=list(project_names.keys()))
#         project_id = project_names[selected_project]
#     else:
#         st.error("無法獲取工程專案列表")
#         return

#     # 上傳抽查表
#     with st.form("inspection_form"):
#         name = st.text_input("抽查表名稱", placeholder="例如：基礎開挖抽查")
#         inspection_time = st.date_input("抽查日期", value=datetime.now())
#         location = st.text_input("抽查地點", placeholder="例如：A區基礎開挖面")
#         uploaded_file = st.file_uploader("上傳抽查表PDF", type=["pdf"])
        
#         submit_button = st.form_submit_button("提交")
        
#         if submit_button and uploaded_file is not None:
#             # 創建臨時文件來保存上傳的PDF
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#                 tmp_file.write(uploaded_file.getvalue())
#                 tmp_file_path = tmp_file.name
            
#             # 創建抽查記錄
#             inspection_data = {
#                 "name": name,
#                 "inspection_time": f"{inspection_time}T00:00:00",
#                 "location": location,
#                 "file_path": "",  # 先創建記錄，稍後更新文件路徑
#                 "project_id": project_id
#             }
            
#             response = utils.create_data("inspections", inspection_data)
#             if response:
#                 inspection_id = response["id"]
                
#                 # 上傳PDF文件
#                 files = {"file": ("inspection.pdf", open(tmp_file_path, "rb"), "application/pdf")}
#                 upload_response = utils.upload_file(
#                     f"{API_URL}/inspections/upload",
#                     files,
#                     data={"project_id": project_id, "inspection_id": inspection_id}
#                 )
                
#                 if upload_response:
#                     st.success("抽查表上傳成功！")
#                 else:
#                     st.error("文件上傳失敗")
                
#                 # 清理臨時文件
#                 os.unlink(tmp_file_path)
#             else:
#                 st.error("創建抽查記錄失敗")

# def view_inspections():
#     st.subheader("已上傳的抽查表")
    
#     # 選擇工程專案
#     projects = utils.fetch_data("projects", project_id=None)
#     if projects:
#         project_names = {f"{p['name']} ({p['contract_number']})": p['id'] for p in projects}
#         selected_project = st.selectbox("選擇工程專案", options=list(project_names.keys()), key="view_project")
#         project_id = project_names[selected_project]
        
#         # 獲取該專案的抽查記錄
#         inspections = utils.fetch_data("inspections", project_id)
#         if inspections:
#             if not inspections:
#                 st.info("尚無抽查記錄")
#                 return
            
#             # 顯示抽查記錄列表
#             for inspection in inspections:
#                 with st.expander(f"{inspection['name']} - {inspection['inspection_time'][:10]}"):
#                     col1, col2, col3 = st.columns(3)
                    
#                     with col1:
#                         st.write(f"地點：{inspection['location']}")
                    
#                     with col2:
#                         if st.button("下載PDF", key=f"download_{inspection['id']}"):
#                             response = utils.fetch_data("inspections", inspection['id']+"/download")
#                             if response.status_code == 200:
#                                 # 提供下載連結
#                                 st.download_button(
#                                     "點擊下載",
#                                     response.content,
#                                     f"inspection_{inspection['id']}.pdf",
#                                     "application/pdf"
#                                 )
                    
#                     with col3:
#                         if st.button("刪除", key=f"delete_{inspection['id']}"):
#                             if st.warning("確定要刪除這份抽查表嗎？"):
#                                 response = utils.delete_data("inspections", inspection['id'])
#                                 if response.status_code == 200:
#                                     st.success("刪除成功")
#                                     st.experimental_rerun()
#                                 else:
#                                     st.error("刪除失敗")


    
# tab1, tab2 = st.tabs(["上傳抽查表", "查看抽查表"])

# with tab1:
#     upload_inspection()

# with tab2:
#     view_inspections()
