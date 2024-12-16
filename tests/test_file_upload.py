import pytest
from fastapi.testclient import TestClient
from main import app, UPLOAD_DIR
from pathlib import Path
import shutil
import os
from database import Base, engine, SessionLocal, init_db
from datetime import datetime

# 測試客戶端
client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """設置測試數據庫"""
    # 確保測試數據庫目錄存在
    test_db_dir = Path("data")
    test_db_dir.mkdir(exist_ok=True)
    
    # 初始化測試數據庫
    init_db()
    
    yield
    
    # 清理數據庫
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """每個測試前後的設置和清理"""
    # 確保上傳目錄存在
    UPLOAD_DIR.mkdir(exist_ok=True)
    
    yield
    
    # 清理上傳的文件
    if UPLOAD_DIR.exists():
        for item in UPLOAD_DIR.glob("**/*"):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

def create_test_project():
    """創建測試用的工程專案"""
    project_data = {
        "name": "測試工程",
        "contract_number": "TEST-001",
        "contractor": "測試承包商",
        "location": "測試地點"
    }
    response = client.post("/projects/", json=project_data)
    assert response.status_code == 200, f"創建專案失敗: {response.text}"
    return response.json()

def create_test_inspection(project_id: int):
    """創建測試用的抽查記錄"""
    inspection_data = {
        "project_id": project_id,
        "name": "測試抽查",
        "inspection_time": datetime.now().isoformat(),
        "location": "測試地點",
        "file_path": ""
    }
    response = client.post("/inspections/", json=inspection_data)
    assert response.status_code == 200, f"創建抽查記錄失敗: {response.text}"
    return response.json()

def test_upload_inspection_file():
    """測試上傳抽查文件"""
    # 創建測試數據
    project = create_test_project()
    inspection = create_test_inspection(project["id"])
    
    # 創建測試文件
    test_file_content = b"Test file content"
    files = {"file": ("test.pdf", test_file_content, "application/pdf")}
    
    # 上傳文件
    response = client.post(
        "/upload-inspection-file/",
        files=files,
        params={
            "project_id": project["id"],
            "inspection_id": inspection["id"]
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "filename" in result
    assert "file_path" in result
    assert Path(result["file_path"]).exists()

def test_upload_inspection_file_no_project():
    """測試上傳文件時沒有提供專案ID"""
    # 創建測試文件
    test_file_content = b"Test file content"
    files = {"file": ("test.pdf", test_file_content, "application/pdf")}
    
    # 上傳文件，不提供project_id
    response = client.post(
        "/upload-inspection-file/",
        files=files,
        params={"inspection_id": 999}
    )
    
    assert response.status_code == 400
    assert "必須提供 project_id" in response.json()["detail"]

def test_download_inspection_file():
    """測試下載抽查文件"""
    # 創建測試數據
    project = create_test_project()
    inspection = create_test_inspection(project["id"])
    
    # 上傳文件
    test_file_content = b"Test file content"
    files = {"file": ("test.pdf", test_file_content, "application/pdf")}
    
    upload_response = client.post(
        "/upload-inspection-file/",
        files=files,
        params={
            "project_id": project["id"],
            "inspection_id": inspection["id"]
        }
    )
    assert upload_response.status_code == 200
    
    # 下載文件
    download_response = client.get(f"/download-inspection-file/{inspection['id']}")
    assert download_response.status_code == 200
    assert download_response.content == test_file_content

def test_download_nonexistent_file():
    """測試下載不存在的文件"""
    response = client.get("/download-inspection-file/999")
    assert response.status_code == 404

def test_upload_invalid_file_type():
    """測試上傳無效的文件類型"""
    project = create_test_project()
    inspection = create_test_inspection(project["id"])
    
    # 創建一個無效類型的文件
    test_file_content = b"Invalid file content"
    files = {"file": ("test.exe", test_file_content, "application/x-msdownload")}
    
    response = client.post(
        "/upload-inspection-file/",
        files=files,
        params={
            "project_id": project["id"],
            "inspection_id": inspection["id"]
        }
    )
    
    assert response.status_code == 400
    assert "不支持的文件類型" in response.json()["detail"]
