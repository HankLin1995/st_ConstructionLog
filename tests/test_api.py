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
from models import Project, ContractItem, QualityTest, Inspection, Photo

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

def test_update_project(client):
    """測試更新工程專案"""
    # 先創建一個測試項目
    response = client.post(
        "/projects/",
        json={
            "name": "Test Project",
            "contract_number": "TEST-002",
            "contractor": "Test Contractor",
            "location": "Test Location"
        }
    )
    project_id = response.json()["id"]
    
    # 更新項目
    update_response = client.put(
        f"/projects/{project_id}",
        json={
            "name": "Updated Project",
            "contractor": "Updated Contractor"
        }
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Project"
    assert data["contractor"] == "Updated Contractor"
    assert data["contract_number"] == "TEST-002"  # 未更新的欄位應保持不變

def test_delete_project(client):
    """測試刪除工程專案"""
    # 先創建一個測試項目
    response = client.post(
        "/projects/",
        json={
            "name": "Test Project",
            "contract_number": "TEST-003",
            "contractor": "Test Contractor",
            "location": "Test Location"
        }
    )
    project_id = response.json()["id"]
    
    # 刪除項目
    delete_response = client.delete(f"/projects/{project_id}")
    assert delete_response.status_code == 200
    
    # 確認項目已被刪除
    get_response = client.get(f"/projects/{project_id}")
    assert get_response.status_code == 404

def test_create_photo(client):
    """測試創建圖片記錄"""
    # 先創建一個測試項目
    project_response = client.post(
        "/projects/",
        json={
            "name": "Test Project",
            "contract_number": "TEST-004",
            "contractor": "Test Contractor",
            "location": "Test Location"
        }
    )
    project_id = project_response.json()["id"]

    response = client.post(
        "/photos/",
        json={
            "filename": "test.jpg",
            "file_path": "/uploads/test.jpg",
            "description": "Test Photo",
            "project_id": project_id,
            "quality_test_id": None,
            "inspection_id": None
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.jpg"
    assert data["project_id"] == project_id

def test_update_photo(client):
    """測試更新圖片記錄"""
    # 先創建測試項目和圖片
    project_response = client.post(
        "/projects/",
        json={
            "name": "Test Project",
            "contract_number": "TEST-005",
            "contractor": "Test Contractor",
            "location": "Test Location"
        }
    )
    project_id = project_response.json()["id"]

    photo_response = client.post(
        "/photos/",
        json={
            "filename": "test.jpg",
            "file_path": "/uploads/test.jpg",
            "description": "Test Photo",
            "project_id": project_id,
            "quality_test_id": None,
            "inspection_id": None
        }
    )
    photo_id = photo_response.json()["id"]

    # 更新圖片
    response = client.put(
        f"/photos/{photo_id}",
        json={
            "filename": "updated.jpg",
            "description": "Updated Photo"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "updated.jpg"
    assert data["description"] == "Updated Photo"

def test_read_project_photos(client):
    """測試讀取項目圖片"""
    # 先創建測試項目和圖片
    project_response = client.post(
        "/projects/",
        json={
            "name": "Test Project",
            "contract_number": "TEST-006",
            "contractor": "Test Contractor",
            "location": "Test Location"
        }
    )
    project_id = project_response.json()["id"]

    # 創建兩張圖片
    for i in range(2):
        client.post(
            "/photos/",
            json={
                "filename": f"test{i}.jpg",
                "file_path": f"/uploads/test{i}.jpg",
                "description": f"Test Photo {i}",
                "project_id": project_id,
                "quality_test_id": None,
                "inspection_id": None
            }
        )

    # 讀取項目圖片
    response = client.get(f"/projects/{project_id}/photos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_delete_photo(client):
    """測試刪除圖片"""
    # 先創建測試項目和圖片
    project_response = client.post(
        "/projects/",
        json={
            "name": "Test Project",
            "contract_number": "TEST-007",
            "contractor": "Test Contractor",
            "location": "Test Location"
        }
    )
    project_id = project_response.json()["id"]

    photo_response = client.post(
        "/photos/",
        json={
            "filename": "test.jpg",
            "file_path": "/uploads/test.jpg",
            "description": "Test Photo",
            "project_id": project_id,
            "quality_test_id": None,
            "inspection_id": None
        }
    )
    photo_id = photo_response.json()["id"]

    # 刪除圖片
    response = client.delete(f"/photos/{photo_id}")
    assert response.status_code == 200

    # 確認圖片已被刪除
    response = client.get(f"/projects/{project_id}/photos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
