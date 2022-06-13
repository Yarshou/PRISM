import io
import os

import PIL
import face_recognition
from PIL import Image, ImageDraw
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from analyze.models import Photo, Encodings, Event
from analyze.serializers import PhotoListSerializer
from authentication.models import User
from core import settings
from dashboard.serializers import EventSerializer


class AvatarListView(generics.RetrieveAPIView):
    queryset = Photo.objects.all()
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if kwargs.get('id'):
            try:
                user = User.objects.get(id=kwargs.get('id'))
            except User.DoesNotExist:
                return Response({'detail': 'user does not exists'})
        else:
            user = request.user

        try:
            user_photo = Photo.objects.get(
                id__in=Encodings.objects.filter(user=user).select_related('related_photos').values_list('photo_id',
                                                                                                        flat=True),
                is_avatar=True
            )
        except Photo.DoesNotExist:
            return Response({'detail': 'user has no avatar'})

        base_dir = settings.MEDIA_URL

        return Response({'images': [os.path.join(base_dir, str(user_photo.img))]}, status=status.HTTP_200_OK)


class EventListView(generics.RetrieveAPIView):
    lookup_url_kwarg = 'event_name'
    lookup_field = 'name'

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):

        if kwargs.get('event_name'):
            photos = Photo.objects.filter(event=Event.objects.get(name=kwargs.get('event_name'))).select_related(
                'event')
            serializer = PhotoListSerializer(
                data=[{'id': photo.id, 'img': photo.img, 'event': kwargs.get('event_name')} for photo in photos],
                many=True)

            if not serializer.is_valid():
                return Response({'detail': 'invalid request'}, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data)

        return Response({'events': [event.name for event in self.get_queryset()]})


class UserPhotoListView(generics.RetrieveAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoListSerializer

    def get(self, request, *args, **kwargs):

        if kwargs.get('event'):
            photos = Photo.objects.filter(id__in=Encodings.objects.filter(user=request.user).values_list('photo_id'),
                                          event=Event.objects.get(name=kwargs.get('event')))
            serializer = self.serializer_class(data=[{'img': photo.img} for photo in photos], many=True)
            if serializer.is_valid():
                return Response({'images': serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'event were not provided'})


@permission_classes((IsAuthenticated,))
@api_view(['POST', ])
def make_request(request, *args, **kwargs):
    from moderator.models import UserRequest

    if not request.data:
        return Response({'payload': 'no data'}, status=status.HTTP_400_BAD_REQUEST)

    enc_id = request.data.get('enc_id', None)
    locations = request.data.get('locations', None)
    photo_id = request.data.get('photo_id', None)

    if not enc_id or not locations or not photo_id:
        return Response({'payload': 'no data'}, status=status.HTTP_400_BAD_REQUEST)

    img_name = str(Photo.objects.get(id=photo_id).img).split('/').pop()
    thumbnail = 'media/thumbnails/thumbnail_' + img_name
    thumbnail = face_recognition.load_image_file(thumbnail)
    pillow_img = Image.fromarray(thumbnail)
    draw = ImageDraw.Draw(pillow_img)

    for (top, right, bottom, left) in [locations, ]:
        draw.rectangle(((left, top), (right, bottom)), outline=(255, 255, 0), width=4)
    del draw

    pillow_img.save(f'media/rected/thumbnail_rected_{img_name}')
    pillow_io = io.BytesIO()
    pillow_img.save(pillow_io, format='jpeg')
    pillow_io.seek(0)

    UserRequest.objects.create(
        user=request.user,
        status=False,
        vector=Encodings.objects.get(pk=enc_id),
        locations=locations,
        rected_image=InMemoryUploadedFile(
            pillow_io,
            'ImageField',
            f'thumbnail_rected_{img_name}',
            'image/jpeg',
            pillow_img.tell(),
            None
        )
    )

    return Response({'status': 'ok'})
