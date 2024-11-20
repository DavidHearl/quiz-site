from django.urls import path
from .views import active_quiz, next_flag, previous_flag

urlpatterns = [
    path('', active_quiz, name='active_quiz'),
    path('next/', next_flag, name='next_flag'),
    path('previous/', previous_flag, name='previous_flag'),
]