import face_recognition
from rest_framework import serializers

from analyze.models import Photo
from analyze.utils.validators import PhotoValidator


class PhotoSerializer(serializers.Serializer):
    img = serializers.ImageField(required=True)
    is_avatar = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Photo
        fields = (
            'img',
        )

    def validate_img(self, img):
        validator = PhotoValidator(img)
        if not validator.photo_has_face():
            raise serializers.ValidationError('There must be at least one person in the photo')

    def create(self, validated_data):
        return Photo.objects.create(**validated_data)
