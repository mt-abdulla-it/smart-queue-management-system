"""Dashboard URL stubs — will be fully implemented in Phases 5 & 8."""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),
]
