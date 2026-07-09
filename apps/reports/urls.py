from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('export/excel/', views.ExportExcelView.as_view(), name='export_excel'),
    path('export/pdf/', views.ExportPDFView.as_view(), name='export_pdf'),
]
