from app.models import mysql_model as my_models
from app.schemas import ClassificationRecord
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

async def test_connection(db: AsyncSession):
    try:
        # 測試資料庫連線 1+1
        stmt = select(1 + 1)
        result = await db.execute(stmt)
        return result is not None
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False

async def create_classification_record(db: AsyncSession, record: ClassificationRecord):
    print(record)
    new_record = my_models.DrillMapAIPredictionRecord(**record)
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    return True

async def get_classification_record_check(db: AsyncSession, image_path: str):
    stmt = select(my_models.DrillMapAIPredictionRecord).filter(my_models.DrillMapAIPredictionRecord.image_path == image_path)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_classification_record_by_datetime(db: AsyncSession, start_time: str, end_time: str):
    stmt = select(my_models.DrillMapAIPredictionRecord).filter(
        my_models.DrillMapAIPredictionRecord.classification_time >= start_time,
        my_models.DrillMapAIPredictionRecord.classification_time <= end_time
    )
    result = await db.execute(stmt)
    return result.scalars().all()