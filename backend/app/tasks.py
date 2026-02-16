import os
import face_recognition
from database import SessionLocal
from models import Photo,FaceEmbedding
from celery import celery
from sqlalchemy.orm import Session
from backend.celery_app import celery
from ml.encoder import extract_face_embeddings

def process_photos(photo_id):
    db=SessionLocal()
    
    try:
        photo=db.query(Photo).filter(Photo.id==photo_id).first()
        
        if not photo:
            print('Photo not found..')
            return
        
        if not os.path.exists(photo.storage_url):
            print('Image file missing..')
            return
        
        image=face_recognition.load_image_file(photo.storage_url)
        
        faces=extract_face_embeddings(image)
        for face in faces:
            embedding_record= FaceEmbedding(
                photo_id=photo_id,
                embedding=face['embedding']
            )
            db.add(embedding_record)
            
        if hasattr(photo,'processed'):
            photo.processed=True
            
        db.commit()
        
    except Exception as e:
        db.rollback()
        print("[WORKER ERROR]",str(e))
        
    finally:
        db.close()
        