from typing import List

import face_recognition
import numpy as np


def encode_photo(img) -> List[np.ndarray]:
    img = face_recognition.load_image_file(img)
    return face_recognition.face_encodings(img)
