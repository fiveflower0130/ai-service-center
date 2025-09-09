from app.tasks.celery_app import celery_app

@celery_app.task(bind=True, name='app.tasks.api_tasks.test_sync_requests_to_async_api')
def test_sync_requests_to_async_api(self):
    """測試同步 requests 調用異步 API"""
    try:
        import requests
        
        self.update_state(state='PROGRESS', meta={'progress': 0, 'status': '開始測試同步'})
        # 同步調用異步 API
        response = requests.get("http://localhost:8009/drill_map/test_sync_call")

        # 檢查回應狀態碼
        self.update_state(state='SUCCESS', meta={'progress': 100, 'status': '處理完成'})
        
        if response.status_code == 200:
            data = response.json()
            return f"成功調用：{data}"
        else:
            return f"調用失敗：{response.status_code}"
            
    except Exception as e:
        return f"錯誤：{str(e)}"