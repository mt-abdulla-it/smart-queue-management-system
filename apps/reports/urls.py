from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('analytics/', views.AnalyticsDashboardView.as_view(), name='analytics_dashboard'),
    path('export/csv/', views.ExportCSVView.as_view(), name='export_csv'),
    path('export/excel/', views.ExportExcelView.as_view(), name='export_excel'),
    path('export/pdf/', views.ExportPDFView.as_view(), name='export_pdf'),
]
