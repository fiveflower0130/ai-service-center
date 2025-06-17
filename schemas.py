from pydantic import BaseModel

class ClassificationRequest(BaseModel):
    img_src: str
    product_name: str