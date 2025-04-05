from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from . import views

urlpatterns = [
    path('loading/', views.loading_page, name='loading_page'),
    path('general_knowledge/', views.general_knowledge, name='general_knowledge'),
    path('edit_general_knowledge/<int:question_id>/', views.edit_general_knowledge, name='edit_general_knowledge'),
    path('true_or_false/', views.true_or_false, name='true_or_false'),
    path('edit_true_or_false/<int:question_id>/', views.edit_true_or_false, name='edit_true_or_false'),
    path('flags/', views.flags, name='flags'),
    path('edit_flags/<int:flag_id>/', views.edit_flags, name='edit_flags'),
    path('logos/', views.logos, name='logos'),
    path('edit_logos/<int:logo_id>/', views.edit_logos, name='edit_logos'),
    path('jets/', views.jets, name='jets'),
    path('edit_jets/<int:jet_id>/', views.edit_jets, name='edit_jets'),
    path('celebrities/', views.celebrities, name='celebrities'),
    path('edit_celebrities/<int:celebrity_id>/', views.edit_celebrities, name='edit_celebrities'),
    path('movies/', views.movies, name='movies'),
    path('edit_movies/<int:movie_id>/', views.edit_movies, name='edit_movies'),
    path('locations/', views.locations, name='locations'),
    path('edit_locations/<int:location_id>/', views.edit_locations, name='edit_locations'),
    path('music/', views.music, name='music'),
    path('edit_music/<int:music_id>/', views.edit_music, name='edit_music'),
]