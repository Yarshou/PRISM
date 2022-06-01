from django.urls import path

from .views import RegistrationAPIView, LoginAPIView, UserRetrieveUpdateAPIView, UserDetailView

app_name = 'authentication'

urlpatterns = [
    path('', UserRetrieveUpdateAPIView.as_view()),
    path('<int:id>', UserDetailView.as_view()),
    path('register/', RegistrationAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
]
