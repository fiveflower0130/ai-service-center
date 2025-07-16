from app.tasks.celery_app import celery_app
from app.database.mysql_database import mysql_session
from icecream import ic
import asyncio
from app.crud.drill_map import test_connection

@celery_app.task(bind=True, name='app.tasks.health_tasks.health_check')
def health_check(self):
    """健康檢查任務 - 測試資料庫連線"""
    try:
        ic("開始執行健康檢查任務")
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': '開始檢查'})
        
        # 執行非同步資料庫查詢
        result = asyncio.run(_health_check())
        
        self.update_state(
            state='SUCCESS', 
            meta={
                'progress': 100, 
                'status': '檢查完成',
                'result': result
            }
        )

        ic(f"健康檢查完成: {result}")
        return result
        
    except Exception as e:
        error_msg = f"健康檢查失敗: {str(e)}"
        ic(error_msg)
        self.update_state(
            state='FAILURE',
            meta={'error': error_msg}
        )
        raise

async def _health_check():
    """非同步健康檢查函式"""
    async with mysql_session() as session:
        try:
            # 執行簡單的 SQL 查詢

            result = await test_connection(session)
            
            return {
                "database_status": "connected",
                "test_query_result": result,
                "message": "資料庫連線正常"
            }
            
        except Exception as e:
            ic(f"資料庫查詢錯誤: {str(e)}")
            return {
                "database_status": "failed",
                "error": str(e),
                "message": "資料庫連線失敗"
            }