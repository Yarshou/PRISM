from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from core import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('authentication.urls')),
    path('api/photo/', include('analyze.urls')),
    path('api/dashboard/', include('dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_URL)
