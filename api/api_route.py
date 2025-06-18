from fastapi import APIRouter, Depends
from ai_modules.drill_map_ai.module import DrillMapAIModule
from .schemas import ClassificationRequest

router = APIRouter()

def get_drill_ai_module():
    from .main import drill_ai_module
    return drill_ai_module

@router.post("/drill_map/classify")
async def classify(
    request: ClassificationRequest,
    module: DrillMapAIModule = Depends(get_drill_ai_module)
):
    return await module.get_ai_classification(request.img_src, request.product_name)