from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from quiz_site.views import home, quiz_home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Make development the home page
    path('create_quiz/', quiz_home, name='quiz_home'),  # Move quiz_home to create_quiz/
    path('quiz/', include('quiz_site.urls')),
    path('accounts/', include('allauth.urls')),
    path('active_quiz/', include(('active_quiz.urls', 'active_quiz'), namespace='active_quiz')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Always serve media files for uploaded content
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)