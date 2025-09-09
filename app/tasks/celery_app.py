from celery import Celery
from app.config import config
from icecream import ic

# 建立 Celery 實例
celery_app = Celery(
    "ai_service_center",
    broker=config.celery_broker_url,
    backend=config.celery_result,
    include=[
        "app.tasks.api_tasks",
        "app.tasks.health_tasks",
        "app.tasks.verification_tasks"
    ]
)

# 設定 Celery 配置
celery_app.conf.update(
    task_serializer="json",  # 設定任務序列化格式
    accept_content=["json"],  # 設定接受的內容類型
    result_serializer="json",  # 設定結果序列化格式
    timezone="Asia/Taipei",  # 設定時區
    enable_utc=True,  # 啟用 UTC 時間
    task_track_started=True,  # 啟用任務啟動追蹤
    task_time_limit=30 * 60,  # 30 分鐘超時
    task_soft_time_limit=25 * 60,  # 25 分鐘軟超時
    
    # 負載平衡
    worker_prefetch_multiplier=1,  # 設定工作預取數量
    worker_max_tasks_per_child=100,  # 每個工作進程最大任務數
    task_acks_late=True,  # 任務完成後再確認
)

# 任務路由設定
celery_app.conf.task_routes = {
    'app.tasks.api_tasks.*': {'queue': 'api'},
    'app.tasks.health_tasks.*': {'queue': 'health'},
    'app.tasks.verification_tasks.*': {'queue': 'verification'},
}

# 定時任務設定
celery_app.conf.beat_schedule = {
    'test-sync-requests-to-async-api-every-3-minutes': {
        'task': 'app.tasks.api_tasks.test_sync_requests_to_async_api',
        'schedule': 180.0,  # 每 3 分鐘執行一次
    },
    'health-check-every-5-minutes': {
        'task': 'app.tasks.health_tasks.health_check',
        'schedule': 300.0,  # 每 5 分鐘執行一次
    },
    # 'verify-recent-predictions-every-6-minutes': {
    #     'task': 'app.tasks.verification_tasks.verify_recent_predictions',
    #     'schedule': 360.0,  # 每 6 分鐘執行一次
    # },
}

ic("Celery 應用初始化完成")
ic(f"Broker URL: {config.celery_broker_url}")
ic(f"Backend URL: {config.celery_result}")