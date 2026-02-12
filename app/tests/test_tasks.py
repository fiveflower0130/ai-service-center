from app.tasks.health_tasks import health_check
from app.tasks.verification_tasks import verify_recent_predictions
from icecream import ic
import time
import asyncio

def test_task_results():
    """測試任務結果獲取"""
    ic("=== 測試任務結果獲取 ===")
    
    # 發送任務
    result = health_check.delay()
    ic(f"任務 ID: {result.id}")
    
    # 獲取任務狀態
    ic(f"任務狀態: {result.status}")
    
    # 獲取任務結果（會等待任務完成）
    task_result = result.get(timeout=30)
    ic(f"任務結果: {task_result}")
    
    return task_result

def test_task_progress():
    """測試任務進度追蹤"""
    ic("=== 測試任務進度追蹤 ===")
    
    # 發送驗證任務
    result = verify_recent_predictions.delay(3)
    ic(f"驗證任務 ID: {result.id}")
    
    # 監控任務進度
    while not result.ready():
        ic(f"任務狀態: {result.status}")
        if result.status == 'PROGRESS':
            ic(f"進度資訊: {result.result}")
        time.sleep(1)
    
    # 獲取最終結果
    final_result = result.get()
    ic(f"最終結果: {final_result}")
    
    return final_result

def test_task_failure():
    """測試任務失敗處理"""
    ic("=== 測試任務失敗處理 ===")
    
    # 這裡可以手動製造一個會失敗的任務來測試
    # 例如傳入無效參數
    try:
        result = verify_recent_predictions.delay(-1) # 負數天數可能會失敗
        task_result = result.get(timeout=30)
        ic(f"任務結果: {task_result}")
    except Exception as e:
        ic(f"任務執行失敗: {e}")
        ic(f"任務狀態: {result.status}")
        ic(f"錯誤追蹤: {result.traceback}")

if __name__ == "__main__":
    # 測試結果獲取
    test_task_results()
    
    # 測試進度追蹤
    test_task_progress()

    # 測試失敗處理
    test_task_failure()