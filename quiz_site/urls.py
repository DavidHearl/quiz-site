from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from . import views

urlpatterns = [
    path('flag/', views.flag, name='flag'),
    path('Logos/', views.Logos, name='Logos'),
]
