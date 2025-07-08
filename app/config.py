import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class Config:
    # MySQL
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = os.getenv("MYSQL_PORT")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    REDIS_DB = os.getenv("REDIS_DB")

    # RabbitMQ
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
    RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")
    RABBITMQ_USER = os.getenv("RABBITMQ_USER")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")

    # Flower
    FLOWER_HOST = os.getenv("FLOWER_HOST")
    FLOWER_PORT = os.getenv("FLOWER_PORT")

    # Application settings
    APP_ENV = os.getenv("APP_ENV")
    APP_DEBUG = os.getenv("APP_DEBUG")
    APP_HOST = os.getenv("APP_HOST")
    APP_PORT = os.getenv("APP_PORT")