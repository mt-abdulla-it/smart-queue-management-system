from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('submit/', views.FeedbackSubmitView.as_view(), name='submit'),
    path('admin-list/', views.AdminFeedbackListView.as_view(), name='admin_list'),
]
