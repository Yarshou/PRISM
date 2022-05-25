from django.urls import path

from analyze import views

app_name = 'authentication'

urlpatterns = [
    path('', views.PhotoListView.as_view({'get': 'list'})),
    path('add/', views.PhotoListView.as_view({'post': 'create'})),
]