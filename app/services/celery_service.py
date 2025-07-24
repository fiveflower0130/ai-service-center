from app.tasks.celery_app import celery_app
from icecream import ic
from typing import Dict, Any, Optional

class CeleryService:
    """Celery 服務封裝類別，提供高階 API"""
    
    def __init__(self):
        self.celery_app = celery_app
    
    def submit_health_check(self) -> str:
        """提交健康檢查任務"""
        task = self.celery_app.send_task('app.tasks.health_tasks.health_check')
        ic(f"健康檢查任務已提交: {task.id}")
        return task.id
    
    def submit_verification_task(self, days: int = 3) -> str:
        """提交驗證任務"""
        task = self.celery_app.send_task(
            'app.tasks.verification_tasks.verify_recent_predictions',
            args=[days]
        )
        ic(f"驗證任務已提交: {task.id}")
        return task.id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """查詢任務狀態"""
        task = self.celery_app.AsyncResult(task_id)
        return {
            "task_id": task_id,
            "status": task.status,
            "result": task.result,
            "info": task.info
        }
    
    def get_worker_stats(self) -> Optional[Dict]:
        """取得 Worker 統計資訊"""
        try:
            inspector = self.celery_app.control.inspect()
            return inspector.stats()
        except Exception as e:
            ic(f"無法取得 Worker 統計: {e}")
            return None

# 建立全域服務實例
celery_service = CeleryService()