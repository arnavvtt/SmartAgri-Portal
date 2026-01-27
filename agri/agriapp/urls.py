from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
path('login/', views.login_view, name='login'),
path('dashboard/', views.dashboard, name='dashboard'),
path('logout/', views.logout_view, name='logout'),

path('weather/', views.weather_view, name='weather'),
path('api/weather/', views.weather_api),

path('crop/add/', views.add_crop, name='add_crop'),
path('crops/', views.my_crops, name='my_crops'),

path('mandi/', views.mandi_view, name='mandi'),

path('register/', views.register_view, name='register'),

path('crop/delete/<int:crop_id>/', views.delete_crop, name='delete_crop'),

path('crop/edit/<int:crop_id>/', views.edit_crop, name='edit_crop')





]
