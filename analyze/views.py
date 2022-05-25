from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from analyze.models import Photo
from analyze.serializers import PhotoSerializer
from analyze.utils.helpers import process_photo


class PhotoListView(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        serializer = PhotoSerializer(data=Photo.objects.all())
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        print(request.data)
        process_photo(request.data.getlist('images'))

        return Response({'detail': 'Photos are currently uploading, please wait'}, status=status.HTTP_200_OK)
