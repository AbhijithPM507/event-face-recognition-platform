import os
from pathlib import Path # Use this for cleaner pathing
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

# The engine is the "central hub" for all database connections
engine = create_async_engine(DATABASE_URL, echo=True)

# This creates a factory that produces a "session" for every API request
SessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession
)

# Every model we create later will inherit from this Base
class Base(DeclarativeBase):
    pass

# Dependency: This is how we give each API route access to the DB
async def get_db():
    async with SessionLocal() as session:
        yield session
        await session.commit()