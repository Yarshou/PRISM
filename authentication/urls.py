from django.urls import path

from .views import RegistrationAPIView, LoginAPIView, UserRetrieveUpdateAPIView

app_name = 'authentication'

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('user/register/', RegistrationAPIView.as_view()),
    path('user/login/', LoginAPIView.as_view()),
]
