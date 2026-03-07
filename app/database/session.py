from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import get_settings
from app.database.models import Base

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Create all tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Dependency — yields a DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
