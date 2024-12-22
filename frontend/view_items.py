import re

from requests import get
import streamlit as st
import pandas as pd
from utils import fetch_data, create_data
import io

def get_project_id():
    st.header("合約項目管理")

    # 獲取專案列表
    projects = fetch_data("projects")
    if not projects:
        st.error("無法獲取專案列表")
        return

    # 選擇專案
    project_names = {p['name']: p['id'] for p in projects}
    selected_project = st.selectbox(
        "選擇工程專案",
        options=list(project_names.keys())
    )
    
    project_id = project_names[selected_project]
    return project_id

# Excel 上傳和導入功能

project_id = get_project_id()

st.subheader("從 Excel 導入合約項目")
uploaded_file = st.file_uploader("上傳 Excel 檔案", type=['xlsx', 'xls'])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        
        # 顯示預覽
        st.write("### 資料預覽")
        st.dataframe(df.head())
        
        # 欄位映射
        st.write("### 欄位映射")
        st.info("請選擇對應的欄位名稱")
        
        columns = list(df.columns)
        item_no = st.selectbox("契約項次", options=columns)
        name = st.selectbox("工項名稱", options=columns)
        unit = st.selectbox("單位", options=columns)
        quantity = st.selectbox("數量", options=columns)
        unit_price = st.selectbox("單價", options=columns)
        total_price = st.selectbox("複價", options=columns)
        
        if st.button("確認導入"):
            # 開始處理數據
            success_count = 0
            error_count = 0
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for index, row in df.iterrows():
                progress = (index + 1) / len(df)
                progress_bar.progress(progress)
                
                try:
                    item_data = {
                        "pcces_code": str(row[item_no]),
                        "name": str(row[name]),
                        "unit": str(row[unit]),
                        "quantity": float(row[quantity]),
                        "unit_price": float(row[unit_price]),
                        "total_price": float(row[total_price]),
                        "project_id": project_id
                    }
                    
                    if create_data("contract-items", item_data):
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    error_count += 1
                    st.error(f"處理第 {index + 1} 行時發生錯誤: {str(e)}")
                
                status_text.text(f"處理進度: {index + 1}/{len(df)}")
            
            st.success(f"導入完成！成功: {success_count} 筆，失敗: {error_count} 筆")
            
    except Exception as e:
        st.error(f"讀取 Excel 檔案時發生錯誤: {str(e)}")

# 顯示現有合約項目
st.subheader("現有合約項目")
items = fetch_data("contract-items", project_id)

if items:
    # 將數據轉換為 DataFrame 以表格形式顯示
    items_df = pd.DataFrame(items)
    items_df = items_df[['pcces_code', 'name', 'unit', 'quantity', 'unit_price', 'total_price']]
    items_df.columns = ['契約項次', '工項名稱', '單位', '數量', '單價', '複價']
    
    # 添加千分位格式
    items_df['單價'] = items_df['單價'].apply(lambda x: f"{x:,.2f}")
    items_df['複價'] = items_df['複價'].apply(lambda x: f"{x:,.2f}")
    
    st.dataframe(
        items_df,
        hide_index=True,
        use_container_width=True
    )
    
    # 匯出功能
    if st.button("匯出為 Excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            items_df.to_excel(writer, index=False, sheet_name='合約項目')
        
        output.seek(0)
        st.download_button(
            label="下載 Excel 檔案",
            data=output,
            file_name=f"{selected_project}_合約項目清單.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("目前沒有合約項目")