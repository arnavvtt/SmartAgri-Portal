from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def crops(request):
    return render(request, 'crops.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def weather(request):
    return render(request, 'weather.html')

def mandi(request):
    return render(request, 'mandi.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')


