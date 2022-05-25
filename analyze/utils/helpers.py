import face_recognition
import numpy as np
from celery import chain

from analyze.models import Photo, Encodings
from analyze.tasks import compare_with_avatars


def encode_photo(img) -> np.ndarray:
    img = face_recognition.load_image_file(img)
    return face_recognition.face_encodings(img)


def create_user_avatar(img, user=None) -> None:
    photo = Photo.objects.create(img=img, is_avatar=True)

    photo_encodings = encode_photo(img)

    encodings_list = list()
    try:
        for enc in photo_encodings:
            encodings_list.append(Encodings(
                vector=enc,
                photo=photo,
                user=user,
            ))
    except Exception as e:
        raise e

    Encodings.objects.bulk_create(encodings_list)


# upload photo -> process photo -> create_photo_raw -> take_encodings -> compare_with_avatars -> compare_with_groups -> if_no_group_create_group
def process_photo(photo_list):
    print('ENTERED PROCESS PHOTO')
    photo_qs = Photo.objects.bulk_create([
        Photo(img=img, is_avatar=False) for img in photo_list
    ])
    encoding_qs = Encodings.objects.bulk_create([
        Encodings(vector=encode_photo(photo), photo=photo) for photo in photo_qs
    ])
    chain(
        compare_with_avatars.s(encodings=encoding_qs),
    ).apply_async()
