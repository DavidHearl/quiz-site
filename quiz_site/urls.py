from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from . import views

urlpatterns = [
    path('flags/', views.flags, name='flags'),
    path('edit_flags/<int:flag_id>/', views.edit_flags, name='edit_flags'),
    path('logos/', views.logos, name='logos'),
    path('edit_logos/<int:logo_id>/', views.edit_logos, name='edit_logos'),
    path('jets/', views.jets, name='jets'),
    path('edit_jets/<int:jet_id>/', views.edit_jets, name='edit_jets'),
    path('celebrities/', views.celebrities, name='celebrities'),
    path('edit_celebrities/<int:celebrity_id>/', views.edit_celebrities, name='edit_celebrities'),
]
