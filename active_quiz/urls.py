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
    path('next_flag/', views.next_flag, name='next_flag'),
    path('next_general_knowledge/', views.next_general_knowledge, name='next_general_knowledge'),
    path('next_history/', views.next_history, name='next_history'),
    path('next_entertainment/', views.next_entertainment, name='next_entertainment'),
    path('next_maths/', views.next_maths, name='next_maths'),
    path('next_pop_culture/', views.next_pop_culture, name='next_pop_culture'),
    path('next_mythology/', views.next_mythology, name='next_mythology'),
    path('next_technology/', views.next_technology, name='next_technology'),
    path('next_geography/', views.next_geography, name='next_geography'),
    path('next_science/', views.next_science, name='next_science'),
    path('next_sport/', views.next_sport, name='next_sport'),
    path('next_capital_city/', views.next_capital_city, name='next_capital_city'),
    path('next_celebrity/', views.next_celebrity, name='next_celebrity'),
    path('next_logo/', views.next_logo, name='next_logo'),
    path('next_true_or_false/', views.next_true_or_false, name='next_true_or_false'),
    path('next_celebrity_age/', views.next_celebrity_age, name='next_celebrity_age'),
    path('next_movie/', views.next_movie, name='next_movie'),
    path('next_movie_release_date/', views.next_movie_release_date, name='next_movie_release_date'),
    path('next_who_is_the_oldest/', views.next_who_is_the_oldest, name='next_who_is_the_oldest'),
    path('next_who_is_the_imposter/', views.next_who_is_the_imposter, name='next_who_is_the_imposter'),
    path('next_fighter_jet/', views.next_fighter_jet, name='next_fighter_jet'),
    path('next_music/', views.next_music, name='next_music'),
    path('next_location/', views.next_location, name='next_location'),
]