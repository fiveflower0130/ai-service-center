from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import asynccontextmanager
from app.config import config

DATABASE_URL = config.async_mysql_url

engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=5,
    max_overflow=10
)
async_session = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)

mysql_base = declarative_base()

# 供API使用的Mysql Session
async def get_mysql_db():
    async with async_session() as session:
        yield session

# 非API使用的Mysql Session
@asynccontextmanager
async def mysql_session():
    async for session in get_mysql_db():
        yield session