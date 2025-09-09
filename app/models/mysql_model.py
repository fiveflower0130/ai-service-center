from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, DateTime, Float
from  app.database.async_mysql_database import mysql_base

class DrillMapAIClassificationRecord(mysql_base):
    __tablename__ = "classification_record"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_row_format": "DYNAMIC"
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    image_path = Column(String(190), index=True)
    product_name = Column(String(64))
    classification_code = Column(String(8))
    classification_model = Column(String(32))
    mahalanobis_distance = Column(Float)
    classification_time = Column(DateTime)

class DrillMapAIPredictionCode(mysql_base):
    __tablename__ = "classification_code"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_general_ci",
        "mysql_row_format": "DYNAMIC"
    }

    code = Column(String(8), primary_key=True, index=True)
    directions = Column(String(64), index=True)
    