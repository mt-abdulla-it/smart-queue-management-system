from django.urls import path
from . import views

app_name = 'queues'

urlpatterns = [
    # User Views
    path('book/', views.BookQueueView.as_view(), name='book'),
    path('my-tokens/', views.MyTokensListView.as_view(), name='my_tokens'),
    path('token/<int:pk>/', views.TokenDetailView.as_view(), name='token_detail'),
    path('token/<int:pk>/pdf/', views.DownloadTokenPDFView.as_view(), name='download_pdf'),
    
    # AJAX Views for dependent dropdowns
    path('ajax/load-departments/', views.load_departments, name='ajax_load_departments'),
    path('ajax/load-services/', views.load_services, name='ajax_load_services'),
    
    # Staff Views
    path('manage/', views.StaffManageQueueView.as_view(), name='staff_manage'),
    path('token/<int:pk>/status/<str:action>/', views.ChangeTokenStatusView.as_view(), name='change_status'),
    
    # Queue Views
    path('history/', views.QueueHistoryListView.as_view(), name='history'),
    path('today/', views.StaffManageQueueView.as_view(), name='today'),
    path('display/', views.LiveDisplayView.as_view(), name='live_display'),
    path('live/', views.LiveDisplayView.as_view(), name='live_display_alias'),
    path('admin-list/', views.AdminQueueListView.as_view(), name='admin_list'),
    
    # API endpoints
    path('api/waiting-list/', views.LiveWaitingListAPIView.as_view(), name='api_waiting_list'),
]
