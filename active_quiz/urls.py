from django.urls import path
from . import views
from .views import check_update

app_name = 'active_quiz'

urlpatterns = [
    path('', views.active_quiz, name='active_quiz'),
    path('check_update/', views.check_update, name='check_update'),
    path('next_flag/', views.next_flag, name='next_flag'),
    path('next_general_knowledge/', views.next_general_knowledge, name='next_general_knowledge'),
]