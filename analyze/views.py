import PIL.Image
import face_recognition
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from analyze.models import Photo, Encodings
from analyze.serializers import PhotoSerializer, PhotoListSerializer
from utils.helpers import process_photo
from utils.validators import PhotoValidator


def get_photo_details(request, **kwargs):
    from PIL import Image
    photo = Photo.objects.get(id=kwargs.get('id'))
    face_image = face_recognition.load_image_file(photo.img)
    resizedImage = Image.fromarray(face_image)
    width, height = resizedImage.size
    resizedImage = resizedImage.resize((int(width/1.5), int(height/1.5)))
    resizedImage.save(f"media/thumbnails/thumbnail_{str(photo.img).split('/').pop()}")
    face_image = face_recognition.load_image_file(f"media/thumbnails/thumbnail_{str(photo.img).split('/').pop()}")
    face_locations = face_recognition.face_locations(face_image)
    encs = list(Encodings.objects.filter(photo=kwargs.get('id')).values_list('id', flat=True))
    zipeer = zip(encs, face_locations)
    new_dict = dict()
    for zipr in zipeer:
        new_dict[zipr[0]] = zipr[1]
    return JsonResponse(new_dict)


class PhotoListView(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):

        if kwargs.get('id'):
            photo = Photo.objects.get(pk=kwargs.get('id'))
            return Response({
                'img': '/media/thumbnails/thumbnail_' + str(photo.img).split('/').pop(),
                'event': photo.event.name})
        else:
            serializer = PhotoListSerializer(
                data=[{'img': photo.img, 'event': photo.event.name} for photo in Photo.objects.filter(is_avatar=False)],
                many=True)

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
