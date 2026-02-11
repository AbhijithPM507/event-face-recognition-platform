import face_recognition
from detector import detect_faces

def extract_face_embeddings(image):
    boxes=detect_faces(image)
    encodings=face_recognition.face_encodings(image,boxes)
    
    result=[]
    
    for box,encoding in zip(boxes,encodings):
        result.append({
            "bbox" : box,
            "embedding" : encoding.tolist()
        })
        
    return result