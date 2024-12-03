from django.urls import path
from . import views
from .views import check_update

app_name = 'active_quiz'

urlpatterns = [
    path('', views.active_quiz, name='active_quiz'),
    path('check_update/', views.check_update, name='check_update'),
    path('next_question/', views.next_question, name='next_question'),
    path('next_celebrity/', views.next_celebrity, name='next_celebrity'),
    path('next_logo/', views.next_logo, name='next_logo'),
    path('next_true_or_false/', views.next_true_or_false, name='next_true_or_false')
]