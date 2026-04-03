from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from ..config.settings import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

AsyncSessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)

Base = declarative_base()

async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session
