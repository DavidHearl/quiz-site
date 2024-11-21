from django.urls import path
from . import views

urlpatterns = [
    path('active_quiz/', views.active_quiz, name='active_quiz'),
    path('next_flag/', views.next_flag, name='next_flag'),
    path('previous_flag/', views.previous_flag, name='previous_flag'),
    path('check_update/', views.check_update, name='check_update'),
]