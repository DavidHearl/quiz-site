from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from . import views

urlpatterns = [
    path('flags/', views.flags, name='flags'),
    path('logos/', views.logos, name='logos'),
]
