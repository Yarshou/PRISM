from rest_framework import viewsets, status
from rest_framework.response import Response

from analyze.models import Photo
from analyze.serializers import PhotoSerializer
from analyze.utils.helpers import process_photo


class PhotoListView(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    def list(self, request, *args, **kwargs):
        serializer = PhotoSerializer(data=Photo.objects.all())
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        process_photo(request.data.getlist('images'))
        raise KeyError
        # serializer = self.serializer_class(data=request.data)
        # try:
        #     for image in request.FILES['images']:
        #         pass
                # if not serializer.is_valid():
                #     return Response(data={'detail': 'img must be uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        # return Response({})
