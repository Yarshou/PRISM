import face_recognition


class PhotoValidator:

    def __init__(self, img):
        img = face_recognition.load_image_file(img)
        self.face_locations = face_recognition.face_locations(img)

    def photo_has_face(self) -> bool:
        return False if not self.face_locations else True

    def photo_has_multiple_faces(self) -> bool:
        return True if len(self.face_locations) > 1 else False
