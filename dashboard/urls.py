from django.urls import path

from dashboard.views import AvatarListView, EventListView, UserPhotoListView

app_name = 'dashboard'

urlpatterns = [
    path('avatar/', AvatarListView.as_view()),
    path('avatar/<int:id>/', AvatarListView.as_view()),
    path('event/', EventListView.as_view()),
    path('event/<str:event_name>', EventListView.as_view()),
    path('user-photos/<str:event>', UserPhotoListView.as_view()),
]
