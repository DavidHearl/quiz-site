from django.contrib import admin
from django.urls import path
from quiz_site.views import quiz_home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', quiz_home, name='quiz_home'),
]
