from django.urls import path
from . import views

app_name = 'branches'

urlpatterns = [
    # Branches
    path('', views.BranchListView.as_view(), name='branch_list'),
    path('add/', views.BranchCreateView.as_view(), name='branch_add'),
    path('<int:pk>/edit/', views.BranchUpdateView.as_view(), name='branch_edit'),
    path('<int:pk>/delete/', views.BranchDeleteView.as_view(), name='branch_delete'),
    
    # Departments
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/add/', views.DepartmentCreateView.as_view(), name='department_add'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_edit'),
    
    # Services
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('services/add/', views.ServiceCreateView.as_view(), name='service_add'),
    path('services/<int:pk>/edit/', views.ServiceUpdateView.as_view(), name='service_edit'),
]
