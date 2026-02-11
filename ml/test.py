import face_recognition
from encoder import extract_face_embeddings
import time

IMAGE_PATH= 'two.jpg'

def main():
    image=face_recognition.load_image_file(IMAGE_PATH)
    print('Processing..')
    start=time.time()
    faces=extract_face_embeddings(image)
    end=time.time()
    
    print(f'Faces detected : {len(faces)}')
    print(f"Time taken: {end-start} seconds..")
    
    for i, face in enumerate(faces):
        print(f"\nFace {i+1}:")
        print("Bounding Box:", face["bbox"])
        print("Embedding length:", len(face["embedding"]))
        
if __name__=="__main__":
    main()