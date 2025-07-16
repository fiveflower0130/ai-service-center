import asyncio
from datetime import datetime, timedelta
from icecream import ic
from app.crud import drill_map as drill_map_crud
from app.tasks.celery_app import celery_app
from app.database.mysql_database import mysql_session



@celery_app.task(bind=True, name='app.tasks.verification_tasks.verify_recent_predictions')
def verify_recent_predictions(self, days=3):
    """驗證最近幾天的預測記錄"""
    try:
        # bind=True時，任務可以訪問自身的上下文，所以function裡面會有self參數，並提供update_state方法
        ic(f"開始驗證最近 {days} 天的預測記錄")
        self.update_state(
            state='PROGRESS', 
            meta={'progress': 0, 'status': f'開始驗證最近 {days} 天的記錄'}
        )
        
        # 執行非同步驗證
        result = asyncio.run(_async_verify_predictions(days))

        self.update_state(
            state='SUCCESS',
            meta={
                'progress': 100, 
                'status': '驗證完成',
                'result': result
            }
        )
        
        ic(f"驗證完成: {result}")
        return result
        
    except Exception as e:
        error_msg = f"驗證任務失敗: {str(e)}"
        ic(error_msg)
        self.update_state(
            state='FAILURE',
            meta={'error': error_msg}
        )
        raise

async def _async_verify_predictions(days):
    """非同步驗證函式"""
    async with mysql_session() as session:
        try:
            # 計算日期範圍
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
            end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
            ic(f"查詢日期範圍: {start_date_str} 到 {end_date_str}")

            # 查詢最近的預測記錄
            verification_result = await drill_map_crud.get_classification_record_by_datetime(
                session, 
                start_date_str, 
                end_date_str
            )

            result = {
                "verification_period": f"{days} 天",
                "start_date": start_date_str,
                "end_date": end_date_str,
                "total_records": len(verification_result) if verification_result else 0,
                "message": "驗證完成"
            }
            
            ic(f"驗證結果: {result}")
            return result
            
        except Exception as e:
            ic(f"驗證查詢錯誤: {str(e)}")
            return {
                "error": str(e),
                "message": "驗證過程中發生錯誤"
            }
