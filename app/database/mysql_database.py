from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import asynccontextmanager

DATABASE_URL = "mysql+asyncmy://5940:5940@192.168.0.101:3306/tid_5940"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)
mysql_base = declarative_base()


async def get_mysql_db():
    async with async_session() as session:
        yield session

@asynccontextmanager
async def mysql_session():
    async for session in get_mysql_db():
        yield session