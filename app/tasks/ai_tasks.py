from app.tasks.celery_app import celery_app
from icecream import ic
import requests
from app.config import config

@celery_app.task(bind=True, name='app.tasks.ai_processing_tasks.process_drill_map_classification')
def process_drill_map_classification(self, img_src: str, product_name: str):
    """純 AI 處理任務，不涉及資料庫操作"""
    try:
        ic(f"開始處理Drill Map AI Service: {img_src}, {product_name}")
        self.update_state(
            state='PROGRESS', 
            meta={'progress': 0, 'status': '開始 AI 處理'}
        )
    except Exception as e:
        error_msg = f"Drill MAP AI Service處理任務失敗: {str(e)}"
        ic(error_msg)
        self.update_state(state='FAILURE', meta={'error': error_msg})
        raise