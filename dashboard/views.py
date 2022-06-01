import os

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
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
                data=[{'img': photo.img, 'event': kwargs.get('event_name')} for photo in photos], many=True)

            if not serializer.is_valid():
                return Response({'detail': 'invalid request'}, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data)

        return Response({'events': [event.name for event in self.get_queryset()]})


class UserPhotoListView(generics.RetrieveAPIView):

    queryset = Photo.objects.all()
    serializer_class = PhotoListSerializer

    def get(self, request, *args, **kwargs):

        if kwargs.get('event'):
            photos = Photo.objects.filter(id__in=Encodings.objects.filter(user=request.user).values_list('photo_id'), event=Event.objects.get(name=kwargs.get('event')))
            serializer = self.serializer_class(data=[{'img': photo.img} for photo in photos], many=True)
            if serializer.is_valid():
                return Response({'images': serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'event were not provided'})
