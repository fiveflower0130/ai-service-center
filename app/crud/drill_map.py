from app.models import mysql_model as my_models
from app.schemas import ClassificationRecord
from sqlalchemy.ext.asyncio import AsyncSession


async def create_classification_record(db: AsyncSession, record: ClassificationRecord):
    print(record)
    new_record = my_models.DrillMapAIPredictionRecord(**record)
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    return True