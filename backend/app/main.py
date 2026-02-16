import shutil
from pathlib import Path as FilePath  # Rename it to avoid the collision
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Path
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from celery import Celery
from app.database import engine, Base, get_db
from app import models, schemas

celery_app = Celery("tasks", broker="redis://localhost:6379/0")
UPLOAD_DIR = FilePath("uploads") 
UPLOAD_DIR.mkdir(exist_ok=True)


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
    try:
        db_event = models.Event(name=event.name, access_code=event.access_code)
        db.add(db_event)
        await db.commit()
        await db.refresh(db_event)
        return db_event
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Access code already exists. Please choose a unique one."
        )
    
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.post("/events/{event_id}/upload", response_model=schemas.PhotoResponse)
async def upload_photo(
    event_id: int, 
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db)
):
    # Unique filename: uploads/eventID_filename
    file_path = UPLOAD_DIR / f"{event_id}_{file.filename}"
    
    # Save the physical file to your local folder
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Write metadata to Postgres
    new_photo = models.Photo(
        event_id=event_id, 
        storage_url=str(file_path),
        processed=False
    )
    db.add(new_photo)
    await db.commit()
    await db.refresh(new_photo)
    
    # THE FINAL HAND-OFF: Push the ID to Redis
    # Dev B's worker will see this and wake up immediately!
    celery_app.send_task("ml_worker.process_photo", args=[new_photo.id])
    
    return new_photo