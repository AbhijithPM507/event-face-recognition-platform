from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

# --- Event Schemas ---
class EventBase(BaseModel):
    name: str

class EventCreate(EventBase):
    access_code: str  # Required when creating

# --- THIS IS THE MISSING ATTRIBUTE ---
class EventResponse(EventBase):
    id: int
    access_code: str
    created_at: datetime
    
    # This tells Pydantic to read data from SQLAlchemy objects
    model_config = ConfigDict(from_attributes=True) 

# --- Photo Schemas ---
class PhotoBase(BaseModel):
    storage_url: str

class PhotoResponse(PhotoBase):
    id: int
    event_id: int
    processed: bool
    model_config = ConfigDict(from_attributes=True)