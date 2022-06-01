from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from analyze.models import Photo
from analyze.serializers import PhotoSerializer, PhotoListSerializer
from analyze.utils.helpers import process_photo
from analyze.utils.validators import PhotoValidator


class PhotoListView(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        serializer = PhotoListSerializer(data=[{'img': photo.img, 'event': photo.event} for photo in Photo.objects.filter(is_avatar=False)], many=True)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)


    def create(self, request, *args, **kwargs):

        images = request.data.getlist('images')
        event = request.data.get('event')

        validator = PhotoValidator()

        for image in images:
            if not validator.photo_has_face(image):
                return Response({'detail': f'No faces were found in the {image} img'})

        process_photo(images, event)

        return Response({'detail': 'Photos are currently uploading, please wait'}, status=status.HTTP_200_OK)
