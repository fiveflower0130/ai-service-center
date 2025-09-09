from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from app.config import config


DATABASE_URL = config.sync_mysql_url
engine = create_engine(
    DATABASE_URL, 
    echo=False, 
    pool_pre_ping=True,      # 新增：自動檢測失效連線
    pool_recycle=3600,       # 新增：1小時回收連線
    pool_size=5,             # 新增：連線池大小
    max_overflow=10          # 新增：最大溢出連線
)
sync_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def mysql_sync_session():
    """同步 MySQL 會話上下文管理器（專門給 Celery 使用）"""
    db = sync_session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()