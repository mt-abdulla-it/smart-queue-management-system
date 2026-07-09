"""
Core App URL Configuration.

Handles the root/home page and any site-wide pages.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
]
