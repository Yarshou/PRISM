from typing import List, Dict

import face_recognition
from django.db.models import Prefetch

from analyze.models import Photo, Encodings, Group
from analyze.utils.utils import encode_photo
from authentication.models import User
from core import celery_app, settings
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@celery_app.task()
def compare_avatar_with_groups(*args, **kwargs):
    groups_qs = Group.objects.filter(user__isnull=True).prefetch_related(
        Prefetch(
            'related_groups',
            queryset=Encodings.objects.all(),
            to_attr='encodings'
        )
    )

    if groups_qs:

        group_encodings_dict = {f'{qs.encodings[0].group.id}': qs.encodings[0].vector for qs in groups_qs}
        avatar_encoding_obj = Encodings.objects.get(id=kwargs.get('avatar_encoding_id'))

        for group_id, group_encoding in group_encodings_dict.items():
            if any(face_recognition.compare_faces([group_encoding, ], avatar_encoding_obj.vector)):
                Encodings.objects.filter(group_id=group_id).update(user=User.objects.get(id=kwargs.get('user_id')))
                return None


@celery_app.task()
def create_encodings(photo_ids) -> List[int]:
    encodings_list = list()

    for photo in Photo.objects.filter(id__in=photo_ids):
        for encoding in encode_photo(photo.img):
            encodings_list.append(Encodings(
                vector=encoding,
                photo=photo
            ))
    tmp = [enc.id for enc in Encodings.objects.bulk_create(encodings_list)]
    return tmp


@celery_app.task()
def compare_with_avatars(*args, **kwargs) -> List[int]:
    photos_qs = Photo.objects.filter(is_avatar=True).prefetch_related(
        Prefetch(
            'related_photos',
            queryset=Encodings.objects.all(),
            to_attr='encodings'
        )
    )

    avatar_encodings_dict = {f'{qs.encodings[0].user.id}': qs.encodings[0].vector for qs in photos_qs}
    photo_encodings_dict = {f'{enc.id}': enc.vector for enc in Encodings.objects.filter(id__in=args[0])}

    group_comparison_encodings_list = list()

    for user_id, avatar_encoding in avatar_encodings_dict.items():
        for encoding_id, encoding_vector in photo_encodings_dict.items():
            if any(face_recognition.compare_faces([avatar_encoding, ], encoding_vector)):
                enc_obj = Encodings.objects.get(id=encoding_id)
                enc_obj.user = User.objects.get(id=user_id)
                enc_obj.save()
            else:
                group_comparison_encodings_list.append(
                    encoding_id) if encoding_id not in group_comparison_encodings_list else None

    return group_comparison_encodings_list


@celery_app.task()
def compare_with_groups(*args, **kwargs):

    groups_qs = Group.objects.filter(user__isnull=True).prefetch_related(
        Prefetch(
            'related_groups',
            queryset=Encodings.objects.all(),
            to_attr='encodings'
        )
    )

    new_encodings = Encodings.objects.filter(id__in=args[0])

    for enc in new_encodings:
        has_group = False
        for group in groups_qs:
            if any(face_recognition.compare_faces([qs.vector for qs in group.encodings], enc.vector)):
                enc.group = group
                enc.save()
                has_group = True
                break

        if not has_group:
            new_group = Group.objects.create()
            enc.group = new_group
            enc.save()
