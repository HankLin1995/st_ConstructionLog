# 2023-12-16: 更新了 API 實現以提高代碼質量
# 1. 更新了模型導入方式，直接從 models 導入具體類
# 2. 將 dict() 方法更新為 model_dump() 以符合 Pydantic v2 的要求
# 3. 更新了所有使用 Test 類的地方為 QualityTest

from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import SessionLocal, engine, init_db
from models import Project, ContractItem, QualityTest, Inspection
import schemas
from typing import List
import logging
from datetime import datetime

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title="工程品質管理系統",
    description="用於管理工程專案、契約項目、品質試驗和施工抽查的 API",
    version="1.0.0"
)

# 初始化數據庫
init_db()

# 依賴注入：獲取數據庫會話
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Project endpoints
@app.post("/projects/", response_model=schemas.Project, tags=["projects"])
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """創建新的工程專案"""
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects/", response_model=List[schemas.Project], tags=["projects"])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """獲取工程專案列表"""
    projects = db.query(Project).offset(skip).limit(limit).all()
    return projects

@app.get("/projects/{project_id}", response_model=schemas.ProjectWithRelations, tags=["projects"])
def read_project(project_id: int, db: Session = Depends(get_db)):
    """獲取特定工程專案的詳細信息，包括關聯數據"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# Contract Item endpoints
@app.post("/contract-items/", response_model=schemas.ContractItem, tags=["contract items"])
def create_contract_item(item: schemas.ContractItemCreate, db: Session = Depends(get_db)):
    """創建新的契約項目"""
    db_item = ContractItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/projects/{project_id}/contract-items/", response_model=List[schemas.ContractItem], tags=["contract items"])
def read_contract_items(project_id: int, db: Session = Depends(get_db)):
    """獲取特定工程專案的契約項目列表"""
    items = db.query(ContractItem).filter(ContractItem.project_id == project_id).all()
    return items

# Test endpoints
@app.post("/tests/", response_model=schemas.Test, tags=["tests"])
def create_test(test: schemas.TestCreate, db: Session = Depends(get_db)):
    """創建新的品質試驗記錄
    
    注意：使用 QualityTest 模型替代原來的 Test 模型
    """
    db_test = QualityTest(**test.model_dump())
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

@app.get("/projects/{project_id}/tests/", response_model=List[schemas.Test], tags=["tests"])
def read_project_tests(project_id: int, db: Session = Depends(get_db)):
    """獲取特定工程專案的品質試驗記錄列表"""
    tests = db.query(QualityTest).filter(QualityTest.project_id == project_id).all()
    return tests

@app.get("/contract-items/{item_id}/tests/", response_model=List[schemas.Test], tags=["tests"])
def read_contract_item_tests(item_id: int, db: Session = Depends(get_db)):
    """獲取特定契約項目的品質試驗記錄列表"""
    tests = db.query(QualityTest).filter(QualityTest.contract_item_id == item_id).all()
    return tests

# Inspection endpoints
@app.post("/inspections/", response_model=schemas.Inspection, tags=["inspections"])
def create_inspection(inspection: schemas.InspectionCreate, db: Session = Depends(get_db)):
    """創建新的施工抽查記錄"""
    db_inspection = Inspection(**inspection.model_dump())
    db.add(db_inspection)
    db.commit()
    db.refresh(db_inspection)
    return db_inspection

@app.get("/projects/{project_id}/inspections/", response_model=List[schemas.Inspection], tags=["inspections"])
def read_project_inspections(project_id: int, db: Session = Depends(get_db)):
    """獲取特定工程專案的施工抽查記錄列表"""
    inspections = db.query(Inspection).filter(Inspection.project_id == project_id).all()
    return inspections
