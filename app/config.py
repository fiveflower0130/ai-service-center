import os
from typing import Optional
from dotenv import load_dotenv
from icecream import ic

# 載入環境變數
load_dotenv()

class Config:
    # MySQL 設定
    MYSQL_USER = os.getenv("MYSQL_USER", "5940")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "5940")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "192.168.0.101")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "tid_5940")

    # Redis 設定
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    REDIS_DB = os.getenv("REDIS_DB", "0")

    # RabbitMQ 設定
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")

    # Flower 設定
    FLOWER_HOST = os.getenv("FLOWER_HOST", "localhost")
    FLOWER_PORT = os.getenv("FLOWER_PORT", "5555")

    # Application 設定
    APP_ENV = os.getenv("APP_ENV", "development")
    APP_DEBUG = os.getenv("APP_DEBUG", "True").lower() == "true"
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", "8009"))

    # 組合後的連線字串
    @property
    def mysql_url(self) -> str:
        """組合 MySQL 連線字串"""
        return f"mysql+asyncmy://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    @property
    def redis_url(self) -> str:
        """組合 Redis 連線字串"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        else:
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def rabbitmq_url(self) -> str:
        """組合 RabbitMQ 連線字串"""
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}//"
    
    # Celery 專用設定
    @property
    def celery_broker_url(self) -> str:
        """Celery Broker URL (使用 RabbitMQ)"""
        return self.rabbitmq_url
    
    @property
    def celery_result_backend(self) -> str:
        """Celery Result Backend URL (使用 Redis)"""
        return self.redis_url

# 建立全域設定實例
config = Config()

# Debug 輸出
if config.APP_DEBUG:
    ic("設定載入完成:")
    ic(f"MySQL URL: {config.mysql_url}")
    ic(f"Redis URL: {config.redis_url}")
    ic(f"RabbitMQ URL: {config.rabbitmq_url}")
    ic(f"App Environment: {config.APP_ENV}")
else:
    ic.disable()