from sqlalchemy import Column, Integer, String, ForeignKey, Float, ARRAY, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    access_code = Column(String, unique=True, index=True) # Used for "logging in" to an event
    created_at = Column(DateTime, default=datetime.utcnow)
    
    photos = relationship("Photo", back_populates="event")

class Photo(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    storage_url = Column(String, nullable=False) # Where the image is stored (S3/Local)
    
    event = relationship("Event", back_populates="photos")
    faces = relationship("FaceEmbedding", back_populates="photo")

class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"
    id = Column(Integer, primary_key=True, index=True)
    photo_id = Column(Integer, ForeignKey("photos.id"))
    # Dev B will populate this later with the facial feature numbers
    embedding = Column(ARRAY(Float)) 
    
    photo = relationship("Photo", back_populates="faces")