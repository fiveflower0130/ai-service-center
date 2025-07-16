import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai_modules.drill_map_ai.module import DrillMapAIModule
from app.schemas import ClassificationRequest, ClassificationRecord, Resp
from app.utils.response_helper import resp
from app.crud import drill_map as crud
from app.database.mysql_database import get_mysql_db
from app.app import get_drill_ai_module

router = APIRouter(
    prefix="/drill_map",
    tags=["drill_map_ai"]
)


@router.post("/classify", response_model = Resp, summary="機鑽圖分類")
async def classify(
    request: ClassificationRequest,
    module: DrillMapAIModule = Depends(get_drill_ai_module),
    db: AsyncSession = Depends(get_mysql_db)
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
    try:
        if not request.img_src or not request.product_name:
            return resp("請提供圖片路徑和產品名稱")

        # 獲取AI分類結果
        data = await module.get_ai_classification(request.img_src, request.product_name)
        
        # 建構分類記錄
        classification_record = {
            "image_path" : request.img_src,
            "product_name": request.product_name,
            "classification_code": data.get("classification_code"),
            "classification_model": data.get("classification_model"),
            "mahalanobis_distance": data.get("distance"),
            "classification_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 插入DB儲存
        insert_result = await crud.create_classification_record(db, classification_record)
        print(f"資料已寫入: {insert_result}")
        return resp(None, data)
    
    except Exception as err:
        return resp(str(err))