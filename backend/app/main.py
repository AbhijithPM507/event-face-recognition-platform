from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine, Base, get_db
from app import models, schemas

# This is the "Architect" way to handle startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP: Create Tables ---
    async with engine.begin() as conn:
        # This makes sure models are registered before creating tables
        await conn.run_sync(Base.metadata.create_all)
    print("Backbone: Database tables initialized.")
    yield
    # --- SHUTDOWN: Clean up (if needed) ---
    await engine.dispose()

app = FastAPI(title="GrabPic API", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "alive", "database": "connected"}

@app.post("/events/", response_model=schemas.EventResponse)
async def create_event(event: schemas.EventCreate, db: AsyncSession = Depends(get_db)):
    db_event = models.Event(name=event.name, access_code=event.access_code)
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event