from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('crops/', views.crops, name='crops'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('weather/', views.weather, name='weather'),
    path('mandi/', views.mandi, name='mandi'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
]
