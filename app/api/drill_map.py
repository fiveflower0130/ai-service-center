from fastapi import APIRouter, Depends
from ..ai_modules.drill_map_ai.module import DrillMapAIModule
from .schemas import ClassificationRequest, Resp

router = APIRouter(
    prefix="/drill_map",
    tags=["drill_map_ai"]
)

def get_drill_ai_module():
    from ..app import drill_ai_module
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

@router.post("/classify", response_model = Resp, summary="機鑽圖分類")
async def classify(
    request: ClassificationRequest,
    module: DrillMapAIModule = Depends(get_drill_ai_module)
):
    '''對機鑽圖進行預測分類\n
    Arguments:\n
    - request: ClassificationRequest，包含圖片的URL或本地路徑和產品名稱\n
    - module: DrillMapAIModule，AI模組\n
    Returns:\n
    - Resp，包含狀態碼、錯誤信息和分類結果\n
    正確回應範例: 
    {
        "code": "0",
        "error": "",
        "data": {
            "classification_code": "TYPE0",
            "classification_model": "A287570_",
            "distance": 34.691369
        }
    }\n
    其中，classification_code為分類代碼，classification_model為分類模型名稱，distance為距離值。\n
    可能的錯誤回應範例:
    {
        "code": "1",
        "error": "圖片加載失敗"
    }\n
    這表示圖片加載失敗，無法進行分類。\n
    '''
    data = await module.get_ai_classification(request.img_src, request.product_name)
    return resp(None, data)