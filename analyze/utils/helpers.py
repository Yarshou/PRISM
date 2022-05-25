from celery import chain

from analyze.models import Photo, Encodings
from analyze.tasks import compare_with_avatars, create_encodings, compare_with_groups, compare_avatar_with_groups
from analyze.utils.utils import encode_photo


def create_user_avatar(img, user=None) -> None:
    photo = Photo.objects.create(img=img, is_avatar=True)

    photo_encodings = encode_photo(img)

    avatar_encoding_obj = Encodings.objects.create(
        vector=photo_encodings[0],
        photo=photo,
        user=user
    )

    compare_avatar_with_groups.apply_async(kwargs={'avatar_encoding_id': avatar_encoding_obj.id, 'user_id': user.id})



def process_photo(photo_list) -> None:
    photo_queryset = Photo.objects.bulk_create([
        Photo(img=img, is_avatar=False) for img in photo_list
    ])

    chain(
        create_encodings.s([photo.id for photo in photo_queryset]),
        compare_with_avatars.s(),
        compare_with_groups.s()
    ).apply_async()
