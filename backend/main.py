# 2023-12-16: 更新了 API 實現以提高代碼質量
# 1. 更新了模型導入方式，直接從 models 導入具體類
# 2. 將 dict() 方法更新為 model_dump() 以符合 Pydantic v2 的要求
# 3. 更新了所有使用 Test 類的地方為 QualityTest

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine, init_db
from models import Project, ContractItem, QualityTest, Inspection, Photo
import schemas
from typing import List, Optional
import logging
from datetime import datetime
import os
from pathlib import Path
import io

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

async def process_uploaded_photo(file: UploadFile, save_path: Path) -> str:
    """處理上傳的照片：保存文件"""
    contents = await file.read()
    
    # 保存原始文件
    with open(save_path, "wb") as f:
        f.write(contents)
    
    return str(save_path)

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

@app.get("/projects/{project_id}", response_model=schemas.ProjectBase, tags=["projects"])
def read_project(project_id: int, db: Session = Depends(get_db)):
    """獲取特定工程專案的詳細信息，包括關聯數據"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.put("/projects/{project_id}", response_model=schemas.Project, tags=["projects"])
def update_project(project_id: int, project_update: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    """更新工程專案"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db_project.updated_at = datetime.now()
    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/projects/{project_id}", tags=["projects"])
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """刪除工程專案"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 刪除相關的契約項目
    db.query(ContractItem).filter(ContractItem.project_id == project_id).delete()
    # 刪除相關的品質試驗
    db.query(QualityTest).filter(QualityTest.project_id == project_id).delete()
    # 刪除相關的施工抽查
    db.query(Inspection).filter(Inspection.project_id == project_id).delete()
    
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}

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

@app.delete("/inspections/{inspection_id}", tags=["inspections"])
def delete_inspection(inspection_id: int, db: Session = Depends(get_db)):
    """刪除施工抽查記錄"""
    db_inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if db_inspection is None:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    db.delete(db_inspection)
    db.commit()
    return {"message": "Inspection deleted successfully"}

# File handling endpoints (RESTful)
@app.post("/inspection-files/", tags=["files"])
async def upload_inspection_file(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    inspection_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """上傳施工抽查相關文件"""
    print(f"project_id: {project_id}, inspection_id: {inspection_id}")
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


@app.get("/inspection-files/{inspection_id}", tags=["files"])
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


@app.delete("/inspection-files/{inspection_id}", tags=["files"])
def delete_inspection_file(inspection_id: int, db: Session = Depends(get_db)):
    """刪除施工抽查相關文件"""
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection or not inspection.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到指定的文件"
        )
    
    file_path = Path(inspection.file_path)
    if file_path.exists():
        file_path.unlink()
    
    # 清空數據庫中的文件路徑
    inspection.file_path = None
    db.commit()
    
    return {"message": "文件刪除成功"}

## 2024-12-29: 新增 Photo endpoints

@app.post("/photos/upload/", response_model=schemas.Photo, tags=["photos"])
async def upload_photo(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    quality_test_id: Optional[str] = Form(None),  
    inspection_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """上傳單張照片並關聯到專案、品質試驗或施工抽查"""
    
    # 驗證檔案類型
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="只允許上傳圖片檔案"
        )
    
    # 處理 quality_test_id
    quality_test_id_int = None
    if quality_test_id and quality_test_id.strip():
        try:
            quality_test_id_int = int(quality_test_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="quality_test_id 必須是有效的整數"
            )
    
    # 建立照片儲存目錄
    photos_dir = UPLOAD_DIR / "photos"
    photos_dir.mkdir(exist_ok=True)
    
    # 生成唯一的檔案名稱
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"{timestamp}_{file.filename}"
    file_path = photos_dir / new_filename
    
    # 處理照片
    file_path_str = await process_uploaded_photo(file, file_path)
    
    # 建立照片記錄
    photo_data = {
        "project_id": project_id,
        "quality_test_id": quality_test_id_int,
        "inspection_id": inspection_id,
        "filename": new_filename,
        "file_path": file_path_str,
        "description": description
    }
    
    db_photo = Photo(**photo_data)
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    
    return db_photo

@app.post("/photos/bulk-upload/", response_model=List[schemas.Photo], tags=["photos"])
async def bulk_upload_photos(
    files: List[UploadFile] = File(...),
    project_id: int = Form(...),
    quality_test_id: Optional[str] = Form(None),  
    inspection_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """批量上傳多張照片"""
    
    # 處理 quality_test_id
    quality_test_id_int = None
    if quality_test_id and quality_test_id.strip():
        try:
            quality_test_id_int = int(quality_test_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="quality_test_id 必須是有效的整數"
            )
    
    photos_dir = UPLOAD_DIR / "photos"
    photos_dir.mkdir(exist_ok=True)
    
    uploaded_photos = []
    
    for file in files:
        # 驗證檔案類型
        if not file.content_type.startswith('image/'):
            continue
        
        # 生成唯一的檔案名稱
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{timestamp}_{file.filename}"
        file_path = photos_dir / new_filename
        
        # 處理照片
        file_path_str = await process_uploaded_photo(file, file_path)
        
        # 建立照片記錄
        photo_data = {
            "project_id": project_id,
            "quality_test_id": quality_test_id_int,
            "inspection_id": inspection_id,
            "filename": new_filename,
            "file_path": file_path_str,
            "description": description
        }
        
        db_photo = Photo(**photo_data)
        db.add(db_photo)
        uploaded_photos.append(db_photo)
    
    db.commit()
    for photo in uploaded_photos:
        db.refresh(photo)
    
    return uploaded_photos

@app.get("/photos/{photo_id}/view", response_class=FileResponse, tags=["photos"])
async def view_photo(photo_id: int, db: Session = Depends(get_db)):
    """查看特定照片"""
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo is None:
        raise HTTPException(status_code=404, detail="照片不存在")
    
    file_path = Path(photo.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="照片檔案不存在")
    
    return FileResponse(file_path)

@app.put("/photos/{photo_id}", response_model=schemas.Photo, tags=["photos"])
def update_photo(photo_id: int, photo: schemas.PhotoUpdate, db: Session = Depends(get_db)):
    """更新圖片"""
    db_photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if db_photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    update_data = photo.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_photo, field, value)
    
    db.commit()
    db.refresh(db_photo)
    return db_photo

@app.get("/projects/{project_id}/photos/", response_model=List[schemas.Photo], tags=["photos"])
def read_project_photos(project_id: int, db: Session = Depends(get_db)):
    """獲取特定工程專案的圖片列表"""
    photos = db.query(Photo).filter(Photo.project_id == project_id).all()
    return photos

@app.get("/inspections/{inspection_id}/photos", response_model=List[schemas.Photo], tags=["photos"])
async def get_inspection_photos(
    inspection_id: int,
    db: Session = Depends(get_db)
):
    """獲取特定施工抽查表下的所有照片"""
    # 檢查施工抽查表是否存在
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if inspection is None:
        raise HTTPException(
            status_code=404,
            detail="施工抽查表不存在"
        )
    
    # 獲取該施工抽查表下的所有照片
    photos = db.query(Photo).filter(Photo.inspection_id == inspection_id).all()
    return photos

@app.delete("/photos/{photo_id}", tags=["photos"])
def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    """刪除圖片"""
    db_photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if db_photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
        
    db.delete(db_photo)
    db.commit()
    return {"message": "Photo deleted successfully"}