from fastapi import APIRouter, Depends
from ai_modules.drill_map_ai.module import DrillMapAIModule
from .schemas import ClassificationRequest, Resp

router = APIRouter(
    prefix="/drill_map",
    tags=["Drill Map AI"]
)

def get_drill_ai_module():
    from .app import drill_ai_module
    return drill_ai_module

# API文件中定義的回傳格式
def resp(errMsg, data=None):
    resp = {"code": "0", "error": ""}

    if errMsg is not None:
        resp["code"] = "1"
        resp["error"] = errMsg
    else:
        resp["data"] = data

    return resp

@router.post("/classify", response_model = Resp)
async def classify(
    request: ClassificationRequest,
    module: DrillMapAIModule = Depends(get_drill_ai_module)
):
    data = await module.get_ai_classification(request.img_src, request.product_name)
    return resp(None, data)