from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from app.models import mysql_model as my_models

def sync_test_connection(db: Session):
    """同步測試資料庫連線"""
    try:
        # 同步版本，不使用 await
        stmt = select(1 + 1)
        result = db.execute(stmt)  # 不使用 await
        return result is not None
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False

def sync_get_classification_record_by_datetime(db: Session, start_time: str, end_time: str):
    """同步取得指定時間範圍的分類記錄"""
    
    stmt = select(my_models.DrillMapAIClassificationRecord).filter(
        my_models.DrillMapAIClassificationRecord.classification_time >= start_time,
        my_models.DrillMapAIClassificationRecord.classification_time <= end_time
    )
    result = db.execute(stmt)
    return result.scalars().all()