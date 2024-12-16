import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from database import Base
from main import app
from main import get_db

# 使用 SQLite 的記憶體模式來建立測試資料庫
# 2023-12-16: 修復了磁盤I/O錯誤，改用內存數據庫替代文件數據庫
# 優點：
# 1. 避免了文件系統權限問題
# 2. 提高了測試速度
# 3. 每次測試都從乾淨的狀態開始
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# 建立測試用的資料庫引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 覆寫資料庫相依性
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# 測試用的客戶端 fixture
@pytest.fixture
def client():
    # 在每個測試開始前建立資料表
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # 在每個測試結束後清除資料表
    Base.metadata.drop_all(bind=engine)
