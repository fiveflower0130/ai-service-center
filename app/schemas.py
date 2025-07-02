from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Any

class Resp(BaseModel):
    code: str
    error: str
    data: Any

class ClassificationRequest(BaseModel):
    img_src: str
    product_name: str

class ClassificationRecord(BaseModel):
    image_path: str
    product_name: str
    classification_code: str
    classification_model: str
    mahalanobis_distance: float
    classification_time: datetime
    
    class Config:
        orm_mode = True