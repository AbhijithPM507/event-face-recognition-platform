import face_recognition

def detect_faces(image):
    faces = face_recognition.face_locations(img=image)
    return faces