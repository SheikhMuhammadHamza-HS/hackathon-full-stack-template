"""Database connection configuration using SQLModel and async PostgreSQL."""
import os
from sqlmodel import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Convert postgresql:// to postgresql+asyncpg:// for async support
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Remove sslmode=require if present, as it conflicts with ssl=True in asyncpg
if "?sslmode=require" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("?sslmode=require", "")
if "&sslmode=require" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("&sslmode=require", "")

DATABASE_ECHO = os.getenv("DATABASE_ECHO", "false").lower() == "true"

# Create async engine with SSL support for Neon
# asyncpg requires ssl parameter instead of sslmode
engine = create_async_engine(
    DATABASE_URL,
    echo=DATABASE_ECHO,
    future=True,
    pool_pre_ping=True,  # Check connection health before using
    pool_size=5,  # Connection pool size
    max_overflow=10,  # Extra connections when pool is full
    connect_args={
        "ssl": True  # Enable SSL for Neon connection
    }
)

# Create async session maker
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session():
    """Dependency for getting async database sessions."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
