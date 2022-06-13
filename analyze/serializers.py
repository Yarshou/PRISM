import face_recognition
from rest_framework import serializers

from analyze.models import Photo, Encodings
from utils.validators import PhotoValidator


class PhotoListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    img = serializers.ImageField(required=True)
    event = serializers.CharField(required=False, allow_blank=True)
    users = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = (
            'id',
            'img',
            'event',
            'users'
        )

    @staticmethod
    def get_users(obj):
        try:
            users = list(Encodings.objects.filter(
                photo=Photo.objects.get(img=obj['img']),
                user__isnull=False
            ).select_related('related_photos').values_list('user_id', flat=True))
        except Exception as e:
            users = []
        return users if users else []



class PhotoSerializer(serializers.Serializer):
    img = serializers.ImageField(required=True)
    event = serializers.CharField(max_length=30, required=True)
    is_avatar = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Photo
        fields = (
            'img',
            'event',
            'is_avatar'
        )

    @staticmethod
    def validate_img(img):
        print('ENTER')
        validator = PhotoValidator()
        print('VALIDATOR FACE: ', validator.photo_has_face(img))
        if not validator.photo_has_face(img):
            raise serializers.ValidationError('There must be at least one person in the photo')

    def create(self, validated_data):
        return Photo.objects.create(**validated_data)
