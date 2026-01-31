from django.urls import path
from . import views

urlpatterns = [
    # Home & Auth
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Dashboard (Enhanced with weather)
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Weather (Detailed analysis)
    path('weather/', views.weather_view, name='weather'),
    path('api/weather/', views.weather_api, name='weather_api'),
    
    # NEW: Crop insight API for AJAX
    path('api/crop-insight/<str:crop_name>/', views.crop_insight_api, name='crop_insight_api'),
    
    # Crop Management
    path('crop/add/', views.add_crop, name='add_crop'),
    path('crops/', views.my_crops, name='my_crops'),
    path('crop/edit/<int:crop_id>/', views.edit_crop, name='edit_crop'),
    path('crop/delete/<int:crop_id>/', views.delete_crop, name='delete_crop'),
    
    # Mandi Prices
    path('mandi/', views.mandi_view, name='mandi'),
    path('farm_planner/', views.farm_planner, name='farm_planner'),

    path('debug-info/', views.debug_view, name='debug_info'),
]
