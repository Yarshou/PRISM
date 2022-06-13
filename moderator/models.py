from django.db import models

from analyze.models import Encodings
from authentication.models import User


class UserRequest(models.Model):
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    vector = models.ForeignKey(Encodings, blank=False, on_delete=models.CASCADE)
    locations = models.TextField(blank=False, null=False)
    rected_image = models.ImageField(upload_to='rected', blank=False, null=False)
