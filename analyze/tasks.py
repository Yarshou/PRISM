import face_recognition
from django.db.models import Prefetch

from analyze.models import Photo, Encodings
from core import celery_app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@celery_app.task()
def compare_with_avatars(*args, **kwargs):
    print('ENTERED TASK')
    photos = Photo.objects.filter(is_avatar=True).prefetch_related(
        Prefetch(
            'related_vectors',
            queryset=Encodings.objects.all(),
            to_attr='encodings'
        )
    )
    encodings_list = [qs.encodings[0].vector for qs in photos]
    if any(face_recognition.compare_faces(encodings_list, kwargs.get('encodings'))):
        print('TRUE')
