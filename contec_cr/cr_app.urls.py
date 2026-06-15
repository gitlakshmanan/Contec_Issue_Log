from django.urls import path
from . import views

urlpatterns = [
    path('', views.cr_list, name='cr_list'),
    path('cr/new/', views.cr_create, name='cr_create'),
    path('cr/<int:pk>/', views.cr_detail, name='cr_detail'),
    path('cr/<int:pk>/edit/', views.cr_edit, name='cr_edit'),
    path('approvals/', views.approval_screen, name='approval_screen'),
    path('approvals/<int:pk>/', views.approve_cr, name='approve_cr'),
    
    # API endpoints
    path('api/cr-data/', views.get_cr_data, name='get_cr_data'),
    path('api/cr/<int:pk>/delete/', views.delete_cr, name='delete_cr'),
]