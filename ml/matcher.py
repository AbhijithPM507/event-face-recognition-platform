import face_recognition

def match_embeddings(known_embedding,new_embedding,threshold=0.6):
    distance=face_recognition.face_distance([known_embedding],new_embedding)[0]
    
    is_match= distance < threshold
    return is_match,float(distance)