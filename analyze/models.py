import numpy as np

from django.db import models
from ndarraydjango.fields import NDArrayField

from django.conf import settings


class Photo(models.Model):
    img = models.ImageField(upload_to='user_media', blank=False, null=False)
    is_avatar = models.BooleanField(default=False)


class Group(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)


class Encodings(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='related_vectors')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    vector = NDArrayField(shape=(128,), dtype=np.float64)

    class Meta:
        unique_together = (('photo', 'vector'),)
