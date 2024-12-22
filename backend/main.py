# 2023-12-16: 更新了 API 實現以提高代碼質量
# 1. 更新了模型導入方式，直接從 models 導入具體類
# 2. 將 dict() 方法更新為 model_dump() 以符合 Pydantic v2 的要求
# 3. 更新了所有使用 Test 類的地方為 QualityTest

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine, init_db
from models import Project, ContractItem, QualityTest, Inspection
import schemas
from typing import List
import logging
from datetime import datetime
import os
from pathlib import Path

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title="工程品質管理系統",
    description="用於管理工程專案、契約項目、品質試驗和施工抽查的 API",
    version="1.0.0"
)

# 設定文件上傳目錄
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # 確保目錄存在

# 允許的文件類型
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx"}

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
    # 驗證 project_id 是否存在
    project = db.query(Project).filter(Project.id == item.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {item.project_id} not found")
        
    db_item = ContractItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/contract-items/", response_model=List[schemas.ContractItem], tags=["contract items"])
def read_contract_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """獲取所有契約項目列表"""
    items = db.query(ContractItem).offset(skip).limit(limit).all()
    return items

@app.get("/projects/{project_id}/contract-items/", response_model=List[schemas.ContractItem], tags=["contract items"])
def read_project_contract_items(project_id: int, db: Session = Depends(get_db)):
    """獲取特定工程專案的契約項目列表"""
    # 驗證 project_id 是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")
        
    items = db.query(ContractItem).filter(ContractItem.project_id == project_id).all()
    return items

@app.put("/contract-items/{item_id}", response_model=schemas.ContractItem, tags=["contract items"])
def update_contract_item(item_id: int, item: schemas.ContractItemUpdate, db: Session = Depends(get_db)):
    """更新契約項目"""
    db_item = db.query(ContractItem).filter(ContractItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Contract item not found")
    
    # 只更新提供的字段
    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/contract-items/{item_id}", tags=["contract items"])
def delete_contract_item(item_id: int, db: Session = Depends(get_db)):
    """刪除契約項目"""
    db_item = db.query(ContractItem).filter(ContractItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Contract item not found")
        
    db.delete(db_item)
    db.commit()
    return {"message": "Contract item deleted successfully"}

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

# File handling endpoints
@app.post("/upload-inspection-file/", tags=["files"])
async def upload_inspection_file(
    file: UploadFile = File(...),
    project_id: int = None,
    inspection_id: int = None,
    db: Session = Depends(get_db)
):
    """上傳施工抽查相關文件"""
    try:
        # 驗證文件類型
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件類型。允許的類型: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        if not project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="必須提供 project_id"
            )
        
        # 創建基於專案ID的子目錄
        project_dir = UPLOAD_DIR / f"project_{project_id}"
        project_dir.mkdir(exist_ok=True)
        
        # 生成唯一的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"inspection_{inspection_id}_{timestamp}{file_extension}"
        file_path = project_dir / unique_filename
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 更新數據庫中的文件路徑
        if inspection_id:
            inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
            if inspection:
                inspection.file_path = str(file_path)
                db.commit()
        
        return {"filename": unique_filename, "file_path": str(file_path)}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上傳失敗: {str(e)}"
        )

@app.get("/download-inspection-file/{inspection_id}", tags=["files"])
async def download_inspection_file(inspection_id: int, db: Session = Depends(get_db)):
    """下載施工抽查相關文件"""
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection or not inspection.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到指定的文件"
        )
    
    file_path = Path(inspection.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/octet-stream"
    )
