
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from pricebook import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pricebook.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='pricebook/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]