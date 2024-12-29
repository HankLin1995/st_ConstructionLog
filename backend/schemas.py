from models import Project, ContractItem, QualityTest, Inspection
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

# Project Schemas
class ProjectBase(BaseModel):
    name: str
    contract_number: str
    contractor: str
    location: str

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    contract_number: Optional[str] = None
    contractor: Optional[str] = None
    location: Optional[str] = None

class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Contract Item Schemas
class ContractItemBase(BaseModel):
    pcces_code: str
    name: str
    unit: str
    quantity: float
    unit_price: float
    total_price: float

class ContractItemCreate(ContractItemBase):
    project_id: int

class ContractItemUpdate(BaseModel):
    pcces_code: Optional[str] = None
    name: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[float] = Field(gt=0, default=None)
    unit_price: Optional[float] = Field(ge=0, default=None)
    total_price: Optional[float] = Field(ge=0, default=None)

class ContractItem(ContractItemBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Test Schemas
class TestBase(BaseModel):
    name: str
    test_item: str
    test_sets: int
    test_result: str

class TestCreate(TestBase):
    project_id: int
    contract_item_id: int

class Test(TestBase):
    id: int
    project_id: int
    contract_item_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Inspection Schemas
class InspectionBase(BaseModel):
    name: str
    inspection_time: datetime
    location: str
    file_path: Optional[str] = None
    is_pass: bool

class InspectionCreate(InspectionBase):
    project_id: int

class Inspection(InspectionBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Photo Schemas
class PhotoBase(BaseModel):
    filename: str
    file_path: str
    description: Optional[str] = None

class PhotoCreate(PhotoBase):
    project_id: int
    quality_test_id: Optional[int] = None
    inspection_id: Optional[int] = None

class PhotoUpdate(BaseModel):
    filename: Optional[str] = None
    description: Optional[str] = None

class Photo(PhotoBase):
    id: int
    project_id: int
    quality_test_id: Optional[int] = None
    inspection_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
