from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import include, path
from quiz_site.views import quiz_home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', quiz_home, name='quiz_home'),
    path('quiz/', include('quiz_site.urls')),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)