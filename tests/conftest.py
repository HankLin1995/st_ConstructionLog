import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base
from main import get_db

# 使用 SQLite 的記憶體模式來建立測試資料庫
# 這樣每次測試都會使用全新的資料庫，不會影響到實際的資料
SQLALCHEMY_DATABASE_URL = "sqlite://"

# 建立測試用的資料庫引擎
# connect_args={"check_same_thread": False} 允許在不同線程中訪問 SQLite
# poolclass=StaticPool 使用靜態連接池，適合測試環境
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# 建立測試用的資料庫 session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """
    提供測試用的資料庫 session
    
    這個 fixture 會:
    1. 在每個測試開始前建立所有資料表
    2. 提供一個資料庫 session 給測試使用
    3. 在測試結束後關閉 session 並刪除所有資料表
    """
    # 建立所有定義在 Base 中的資料表
    Base.metadata.create_all(bind=engine)
    # 建立新的資料庫 session
    db = TestingSessionLocal()
    try:
        # 將 session 提供給測試使用
        yield db
    finally:
        # 測試結束後關閉 session
        db.close()
        # 刪除所有資料表，確保下一個測試有乾淨的環境
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """
    提供測試用的 FastAPI TestClient
    
    這個 fixture 會:
    1. 覆蓋原本的資料庫依賴注入
    2. 提供一個可以發送 HTTP 請求的測試客戶端
    3. 在測試結束後清理所有依賴覆蓋
    
    Args:
        db_session: 由上面的 db_session fixture 提供的資料庫 session
    """
    # 定義一個新的依賴注入函數，使用測試用的 db_session
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    # 覆蓋原本的 get_db 依賴
    app.dependency_overrides[get_db] = override_get_db
    
    # 建立並提供測試客戶端
    with TestClient(app) as test_client:
        yield test_client
    
    # 測試結束後清理所有依賴覆蓋
    app.dependency_overrides.clear()
