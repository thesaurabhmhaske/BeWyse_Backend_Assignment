from django.urls import path
from . import views

urlpatterns = [
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', views.login, name='login'),
    path('accounts/profile/view/', views.profile, name='profile'),
    path('accounts/profile/edit/', views.edit, name='edit'),
]
