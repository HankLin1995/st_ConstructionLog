import streamlit as st
import os

# 從環境變量或默認值配置 API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

# 設置頁面配置
st.set_page_config(

    page_title="工程品質管理系統",
    page_icon="🏗️",
    layout="wide"
)

# 標題和描述
st.title("工程品質管理系統")
st.markdown("統一管理您的工程專案、合約項目和品質測試")

v_projects = st.Page("view_projects.py", title="工程專案", icon=":material/contract:")
v_items=st.Page("view_items.py", title="合約項目", icon=":material/contract:")

pg=st.navigation(
    {
        "專案管理": [v_projects,v_items],
    }
)

pg.run()

# 側邊欄導航
# page = st.sidebar.selectbox(
#     "選擇功能",
#     ["工程專案", "合約項目", "品質測試", "施工抽查"]
# )

# def fetch_data(endpoint, project_id=None):
#     """從 API 獲取數據"""
#     try:
#         url = f"{API_URL}/{endpoint}"
#         if project_id is not None:
#             url = f"{API_URL}/projects/{project_id}/{endpoint}"
#         response = requests.get(url)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             st.error(f"獲取數據失敗：{response.text}")
#             return []
#     except requests.RequestException as e:
#         st.error(f"獲取數據失敗：{str(e)}")
#         return []

# def create_data(endpoint, data):
#     """創建新數據"""
#     try:
#         response = requests.post(
#             f"{API_URL}/{endpoint}",
#             json=data
#         )
#         if response.status_code == 200:
#             st.success("創建成功！")
#             return response.json()
#         else:
#             st.error(f"錯誤：{response.text}")
#             return None
#     except requests.RequestException as e:
#         st.error(f"創建數據失敗：{str(e)}")
#         return None

# def create_inspection():
#     st.header("新增施工抽查紀錄")
    
#     # 獲取專案列表
#     response = requests.get(f"{API_URL}/projects/")
#     if response.status_code == 200:
#         projects = response.json()
#         project_names = {f"{p['name']} ({p['contract_number']})": p['id'] for p in projects}
        
#         selected_project = st.selectbox(
#             "選擇工程專案",
#             options=list(project_names.keys())
#         )
        
#         if selected_project:
#             project_id = project_names[selected_project]
            
#             with st.form("inspection_form"):
#                 name = st.text_input("抽查表名稱")
#                 date = st.date_input("抽查日期", datetime.now())
#                 location = st.text_input("抽查位置")
#                 inspector = st.text_input("抽查人員")
#                 description = st.text_area("抽查內容描述")
#                 result = st.selectbox("抽查結果", ["合格", "不合格"])
                
#                 # 文件上傳
#                 uploaded_file = st.file_uploader("上傳相關文件", type=["pdf", "jpg", "png"])
                
#                 submitted = st.form_submit_button("提交")
                
#                 if submitted:
#                     data = {
#                         "project_id": project_id,
#                         "name": name,
#                         "date": date.strftime("%Y-%m-%d"),
#                         "location": location,
#                         "inspector": inspector,
#                         "description": description,
#                         "result": result
#                     }
                    
#                     if create_data("inspections", data):
#                         st.success("抽查紀錄創建成功！")
#                         if uploaded_file:
#                             st.info("文件上傳功能即將推出...")

# def view_inspections():
#     st.header("查看施工抽查紀錄")
    
#     # 獲取所有專案
#     projects = fetch_data("projects")
#     if projects:
#         # 創建專案選擇框
#         project_names = {f"{p['name']} ({p['contract_number']})": p['id'] for p in projects}
#         selected_project = st.selectbox(
#             "選擇工程專案",
#             options=["全部"] + list(project_names.keys())
#         )
        
#         # 獲取抽查記錄
#         if selected_project == "全部":
#             inspections = fetch_data("inspections")
#         else:
#             project_id = project_names[selected_project]
#             inspections = fetch_data(f"projects/{project_id}/inspections")
        
#         if inspections:
#             for inspection in inspections:
#                 with st.expander(f"{inspection['name']} - {inspection['date']}"):
#                     st.write(f"**位置：** {inspection['location']}")
#                     st.write(f"**抽查人員：** {inspection['inspector']}")
#                     st.write(f"**描述：** {inspection['description']}")
#                     st.write(f"**結果：** {inspection['result']}")
#                     if inspection.get('attachments'):
#                         st.write("**附件：**")
#                         for attachment in inspection['attachments']:
#                             st.write(f"- {attachment['filename']}")
#         else:
#             st.info("暫無抽查記錄")
#     else:
#         st.error("無法獲取專案列表")

# 工程專案管理頁面
# if page == "工程專案":
#     st.header("工程專案管理")
    
#     # 創建新專案表單
#     with st.expander("新增工程專案"):
#         with st.form("project_form"):
#             name = st.text_input("專案名稱")
#             contract_number = st.text_input("合約編號")
#             contractor = st.text_input("施工廠商")
#             location= st.text_input("工程地點")
#             # start_date = st.date_input("開工日期")
#             # end_date = st.date_input("預計完工日期")
#             # description = st.text_area("專案描述")
            
#             submitted = st.form_submit_button("創建專案")
            
#             if submitted:
#                 data={
#                     "name": name,
#                     "contract_number": contract_number,
#                     "contractor": contractor,
#                     "location": location
#                 }

#                 create_data("projects", data)
    
#     # 顯示現有專案
#     projects = fetch_data("projects")
#     if projects:
#         for project in projects:
#             with st.expander(f"{project['name']} ({project['contract_number']})"):
#                 pass
#                 # st.write(f"**開工日期：** {project['start_date']}")
#                 # st.write(f"**預計完工：** {project['end_date']}")
#                 # st.write(f"**描述：** {project['description']}")

# # 合約項目管理頁面
# elif page == "合約項目":
#     st.header("合約項目管理")
    
#     # 獲取專案列表用於過濾
#     projects = fetch_data("projects")
#     if projects:
#         project_names = {p['name']: p['id'] for p in projects}
#         selected_project = st.selectbox(
#             "選擇工程專案",
#             options=list(project_names.keys())
#         )
        
#         project_id = project_names[selected_project]
        
#         # 創建新合約項目表單
#         with st.expander("新增合約項目"):
#             with st.form("contract_item_form"):
#                 item_name = st.text_input("項目名稱")
#                 specification = st.text_input("規格說明")
#                 unit = st.text_input("單位")
#                 quantity = st.number_input("數量", min_value=0.0)
#                 unit_price = st.number_input("單價", min_value=0.0)
                
#                 submitted = st.form_submit_button("新增項目")
                
#                 if submitted:
#                     data = {
#                         "project_id": project_id,
#                         "name": item_name,
#                         "specification": specification,
#                         "unit": unit,
#                         "quantity": quantity,
#                         "unit_price": unit_price
#                     }
#                     create_data("contract_items", data)
        
#         # 顯示該專案的合約項目
#         contract_items = fetch_data("contract_items", project_id)
#         if contract_items:
#             for item in contract_items:
#                 with st.expander(f"{item['name']}"):
#                     st.write(f"**規格：** {item['specification']}")
#                     st.write(f"**單位：** {item['unit']}")
#                     st.write(f"**數量：** {item['quantity']}")
#                     st.write(f"**單價：** {item['unit_price']}")
#                     st.write(f"**總價：** {item['quantity'] * item['unit_price']}")

# # 品質測試管理頁面
# elif page == "品質測試":
#     st.header("品質測試管理")
    
#     # 創建新品質測試表單
#     with st.expander("新增品質測試"):
#         with st.form("quality_test_form"):
#             test_name = st.text_input("測試名稱")
#             test_date = st.date_input("測試日期")
#             test_location = st.text_input("測試位置")
#             test_method = st.text_input("測試方法")
#             test_result = st.text_area("測試結果")
#             pass_fail = st.selectbox("是否合格", ["合格", "不合格"])
            
#             submitted = st.form_submit_button("提交測試結果")
            
#             if submitted:
#                 data = {
#                     "name": test_name,
#                     "date": test_date.strftime("%Y-%m-%d"),
#                     "location": test_location,
#                     "method": test_method,
#                     "result": test_result,
#                     "pass_fail": pass_fail
#                 }
#                 create_data("quality_tests", data)

# # 施工抽查頁面
# elif page == "施工抽查":
#     tab1, tab2 = st.tabs(["新增抽查", "查看記錄"])
    
#     with tab1:
#         create_inspection()
    
#     with tab2:
#         view_inspections()
