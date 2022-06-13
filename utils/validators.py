import face_recognition


class PhotoValidator:

    @staticmethod
    def get_locations(photo):
        img = face_recognition.load_image_file(photo)
        return face_recognition.face_locations(img)

    def photo_has_face(self, img) -> bool:
        return False if not self.get_locations(img) else True

    def photo_has_multiple_faces(self, img) -> bool:
        return True if len(self.get_locations(img)) > 1 else False

