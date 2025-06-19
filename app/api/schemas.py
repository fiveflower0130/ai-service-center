from pydantic import BaseModel
from typing import Optional, Any

class Resp(BaseModel):
    code: str
    error: str
    data: Any

class ClassificationRequest(BaseModel):
    img_src: str
    product_name: str
