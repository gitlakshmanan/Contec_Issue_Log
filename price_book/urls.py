from django.urls import path
from . import views

urlpatterns = [
    path('', views.part_list, name='part_list'),
    path('create/', views.part_create, name='part_create'),
    path('upload-csv/', views.upload_csv, name='upload_csv'),
    path('my-drafts/', views.my_drafts, name='my_drafts'),
    path('<int:pk>/edit/', views.part_update, name='part_update'),
    path('<int:pk>/delete/', views.part_delete, name='part_delete'),
    path('<int:pk>/detail/', views.part_detail, name='part_detail'),
    path('<int:pk>/submit/', views.part_submit_for_review, name='part_submit'),
    
    path('review/', views.review_list, name='review_list'),
    path('review/<int:pk>/', views.review_part, name='review_part'),
    
    path('approval/', views.approval_list, name='approval_list'),
    path('approval/<int:pk>/', views.approve_part, name='approve_part'),
    
    path('ajax/get-part-details/', views.get_part_details, name='get_part_details'),
    path('ajax/create-customer/', views.create_customer_ajax, name='create_customer_ajax'),
    path('ajax/create-po/', views.create_po_ajax, name='create_po_ajax'),
    path('ajax/create-so/', views.create_so_ajax, name='create_so_ajax'),
]
