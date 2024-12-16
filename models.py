# 2023-12-16: 重構了數據模型以提高代碼質量和可維護性
# 1. 將 Test 類重命名為 QualityTest 以避免與 pytest 的命名衝突
# 2. 優化了關聯關係的定義
# 3. 添加了中文註釋以提高可讀性

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from sqlalchemy.sql import func

class Project(Base):
    """工程專案模型"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, comment="工程名稱")
    contract_number = Column(String, unique=True, index=True, comment="契約編號")
    contractor = Column(String, comment="承攬廠商")
    location = Column(String, comment="施工地點")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    contract_items = relationship("ContractItem", back_populates="project")
    tests = relationship("QualityTest", back_populates="project")
    inspections = relationship("Inspection", back_populates="project")

class ContractItem(Base):
    """契約項目模型"""
    __tablename__ = "contract_items"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    pcces_code = Column(String, index=True, comment="PCCES編號")
    name = Column(String, comment="項目名稱")
    unit = Column(String, comment="單位")
    quantity = Column(Float, comment="契約數量")
    unit_price = Column(Float, comment="契約單價")
    total_price = Column(Float, comment="契約複價")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="contract_items")
    tests = relationship("QualityTest", back_populates="contract_item")

class QualityTest(Base):
    """品質試驗紀錄模型
    
    注意：此類原名為 Test，但為避免與 pytest 衝突，已更名為 QualityTest
    """
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    contract_item_id = Column(Integer, ForeignKey("contract_items.id"))
    name = Column(String, comment="自定義試驗名稱")
    test_item = Column(String, comment="對應試驗項目")
    test_sets = Column(Integer, comment="試驗組數")
    test_result = Column(String, comment="試驗結果")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="tests")
    contract_item = relationship("ContractItem", back_populates="tests")

class Inspection(Base):
    """施工抽查紀錄模型"""
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String, comment="抽查表名稱")
    inspection_time = Column(DateTime, comment="抽查時間")
    location = Column(String, comment="抽查地點")
    file_path = Column(String, comment="電子檔路徑")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="inspections")
