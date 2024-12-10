from django.urls import path
from . import views

app_name = 'active_quiz'

urlpatterns = [
    path('', views.active_quiz, name='active_quiz'),
    path('check_update/', views.check_update, name='check_update'),
    path('print_player_data/', views.print_player_data, name='print_player_data'),
    path('quiz_results/', views.quiz_results, name='quiz_results'),
    path('round_results/', views.round_results, name='round_results'),
    path('update_score/', views.update_score, name='update_score'),
    path('next_round/', views.next_round, name='next_round'),
    path('next_question/', views.next_question, name='next_question'),
    path('next_celebrity/', views.next_celebrity, name='next_celebrity'),
    path('next_logo/', views.next_logo, name='next_logo'),
    path('next_true_or_false/', views.next_true_or_false, name='next_true_or_false'),
    path('next_celebrity_age/', views.next_celebrity_age, name='next_celebrity_age'),
    path('next_movie_release_date/', views.next_movie_release_date, name='next_movie_release_date'),
    path('next_who_is_the_oldest/', views.next_who_is_the_oldest, name='next_who_is_the_oldest'),
]