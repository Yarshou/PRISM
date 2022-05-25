import django.core.files.uploadedfile
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
# from .renderers import UserJSONRenderer
from analyze.utils.helpers import create_user_avatar
from analyze.utils.validators import PhotoValidator
from .serializers import RegistrationSerializer, LoginSerializer, UserSerializer


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    # renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer
    # renderer_classes = (UserJSONRenderer,)

    def post(self, request):
        user_avatar = request.data.pop('img', None)
        user_data = request.data
        if user_avatar and isinstance(*user_avatar, django.core.files.uploadedfile.InMemoryUploadedFile):
            validator = PhotoValidator(*user_avatar)
            if not validator.photo_has_face():
                raise Response({'No person were found in the image, try another photo'})
            elif validator.photo_has_multiple_faces():
                raise Response({'There must be one person in the photo'})
        else:
            return Response({'User must have an Avatar'})

        serializer = self.serializer_class(data=user_data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        create_user_avatar(*user_avatar, user=user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    # renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
