import django.core.files.uploadedfile
from django.http import QueryDict
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
# from .renderers import UserJSONRenderer
from utils.helpers import create_user_avatar
from utils.validators import PhotoValidator
from .models import User
from .serializers import RegistrationSerializer, LoginSerializer, UserSerializer


class UserDetailView(RetrieveAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=kwargs.get('id'))
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'detail': 'user does not exists'})


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

        if isinstance(request.data, QueryDict):
            request_data = request.data.dict()
        else:
            request_data = request.data

        print(request_data)
        request_data['is_photographer'] = True if request_data['is_photographer'] == 'true' else False
        print(request_data)

        user_avatar = request_data.pop('img', None)
        user_data = request_data

        if user_avatar and isinstance(user_avatar, django.core.files.uploadedfile.InMemoryUploadedFile):
            validator = PhotoValidator()
            if not validator.photo_has_face(user_avatar):
                return Response({'No person were found in the image, try another photo'}, status=status.HTTP_400_BAD_REQUEST)
            elif validator.photo_has_multiple_faces(user_avatar):
                return Response({'There must be one person in the photo'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'User must have an Avatar'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=user_data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        create_user_avatar(user_avatar, user=user)

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
