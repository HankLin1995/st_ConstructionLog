# 2023-12-16: 更新了測試用例以提高代碼質量和可靠性
# 1. 更新了模型導入，使用 QualityTest 替代 Test
# 2. 修改了測試數據以避免唯一約束衝突
# 3. 優化了測試用例的組織結構

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from database import Base
from main import app, get_db
from models import Project, ContractItem, QualityTest, Inspection

# 測試用資料庫設定
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_create_project(client):
    """測試創建工程專案"""
    response = client.post(
        "/projects/",
        json={
            "name": "Test Project",
            "contract_number": "TEST-001",
            "contractor": "Test Contractor",
            "location": "Test Location"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["contract_number"] == "TEST-001"
    assert "id" in data

def test_read_projects(client):
    """測試讀取工程專案列表"""
    # 先創建一個測試項目
    client.post(
        "/projects/",
        json={
            "name": "Test Project",
            "contract_number": "TEST-001",
            "contractor": "Test Contractor",
            "location": "Test Location"
        }
    )
    
    response = client.get("/projects/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Test Project"

def test_create_contract_item(client):
    """測試創建契約項目"""
    # 先創建一個項目
    project_response = client.post(
        "/projects/",
        json={
            "name": "Test Project",
            "contract_number": "TEST-001",
            "contractor": "Test Contractor",
            "location": "Test Location"
        }
    )
    project_id = project_response.json()["id"]
    
    response = client.post(
        "/contract-items/",
        json={
            "pcces_code": "CODE001",
            "name": "Test Item",
            "unit": "式",
            "quantity": 1.0,
            "unit_price": 1000.0,
            "total_price": 1000.0,
            "project_id": project_id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["project_id"] == project_id

def test_read_contract_items(client):
    """測試讀取契約項目列表"""
    # 先創建項目和契約項目
    project_response = client.post(
        "/projects/",
        json={
            "name": "Test Project",
            "contract_number": "TEST-001",
            "contractor": "Test Contractor",
            "location": "Test Location"
        }
    )
    project_id = project_response.json()["id"]
    
    client.post(
        "/contract-items/",
        json={
            "pcces_code": "CODE001",
            "name": "Test Item",
            "unit": "式",
            "quantity": 1.0,
            "unit_price": 1000.0,
            "total_price": 1000.0,
            "project_id": project_id
        }
    )
    
    response = client.get(f"/projects/{project_id}/contract-items/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Test Item"

def test_create_test(client):
    """測試創建品質試驗記錄"""
    # 先創建項目和契約項目
    project_response = client.post(
        "/projects/",
        json={
            "name": "Test Project",
            "contract_number": "TEST-001",
            "contractor": "Test Contractor",
            "location": "Test Location"
        }
    )
    project_id = project_response.json()["id"]
    
    contract_item_response = client.post(
        "/contract-items/",
        json={
            "pcces_code": "CODE001",
            "name": "Test Item",
            "unit": "式",
            "quantity": 1.0,
            "unit_price": 1000.0,
            "total_price": 1000.0,
            "project_id": project_id
        }
    )
    contract_item_id = contract_item_response.json()["id"]
    
    response = client.post(
        "/tests/",
        json={
            "name": "Test Case",
            "test_item": "Strength Test",
            "test_sets": 3,
            "test_result": "Pass",
            "project_id": project_id,
            "contract_item_id": contract_item_id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Case"
    assert data["project_id"] == project_id
    assert data["contract_item_id"] == contract_item_id

def test_create_inspection(client):
    """測試創建施工抽查記錄
    
    注意：使用不同的 contract_number 以避免唯一約束衝突
    """
    # 先創建一個項目
    project_response = client.post(
        "/projects/",
        json={
            "name": "Test Project for Inspection",
            "contract_number": "TEST-002",
            "contractor": "Test Contractor",
            "location": "Test Location"
        }
    )
    project_id = project_response.json()["id"]
    
    response = client.post(
        "/inspections/",
        json={
            "name": "Test Inspection",
            "inspection_time": "2024-12-16T15:00:00",
            "location": "Test Site",
            "file_path": "/test/path/to/file",
            "project_id": project_id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Inspection"
    assert data["project_id"] == project_id

def test_read_project_with_relations(client):
    """測試讀取工程專案及其關聯數據"""
    # 創建一個完整的項目，包含所有關聯數據
    project_response = client.post(
        "/projects/",
        json={
            "name": "Test Project with Relations",
            "contract_number": "TEST-003",
            "contractor": "Test Contractor",
            "location": "Test Location"
        }
    )
    project_id = project_response.json()["id"]
    
    # 添加契約項目
    client.post(
        "/contract-items/",
        json={
            "pcces_code": "CODE001",
            "name": "Test Item",
            "unit": "式",
            "quantity": 1.0,
            "unit_price": 1000.0,
            "total_price": 1000.0,
            "project_id": project_id
        }
    )
    
    # 添加品質試驗
    client.post(
        "/tests/",
        json={
            "name": "Test Case",
            "test_item": "Strength Test",
            "test_sets": 3,
            "test_result": "Pass",
            "project_id": project_id,
            "contract_item_id": 1
        }
    )
    
    # 添加施工抽查
    client.post(
        "/inspections/",
        json={
            "name": "Test Inspection",
            "inspection_time": "2024-12-16T15:00:00",
            "location": "Test Site",
            "file_path": "/test/path/to/file",
            "project_id": project_id
        }
    )
    
    # 獲取完整的項目數據
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    
    # 驗證關聯數據
    assert len(data["contract_items"]) > 0
    assert len(data["tests"]) > 0
    assert len(data["inspections"]) > 0
