import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# 確保數據目錄存在
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# 根據環境選擇數據庫 URL
SQLALCHEMY_DATABASE_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URL",
    "sqlite:///./data/sql_app.db"
)

# 如果是相對路徑，轉換為絕對路徑
if SQLALCHEMY_DATABASE_URL.startswith("sqlite:///./"):
    db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///./", "")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.abspath(db_path)}"

# 創建數據庫引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 創建會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 創建基類
Base = declarative_base()

def init_db():
    """初始化數據庫"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """獲取數據庫會話"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
