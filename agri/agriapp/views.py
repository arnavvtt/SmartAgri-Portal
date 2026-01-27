from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
import requests
from django.conf import settings
from .forms import CropForm
from .models import Crop
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404

def home(request):
    return render(request, "home.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/dashboard/")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

def logout_view(request):
    logout(request)
    return redirect('/login/')

@login_required
def weather_view(request):
    city = request.GET.get('city', 'Delhi')
    api_key = settings.OPENWEATHER_API_KEY

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=metric"
    )

    response = requests.get(url)
    data = response.json()

    context = {
        "city": city,
        "temp": data.get("main", {}).get("temp"),
        "humidity": data.get("main", {}).get("humidity"),
        "description": data.get("weather", [{}])[0].get("description"),
    }

    return render(request, "weather.html", context)

@login_required
def weather_api(request):
    city = request.GET.get('city')
    api_key = settings.OPENWEATHER_API_KEY

    if not city:
        return JsonResponse({"error": "City required"})

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=metric"
    )

    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        return JsonResponse({"error": "City not found"})

    return JsonResponse({
        "city": city,
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
    })
@login_required
def add_crop(request):
    if request.method == 'POST':
        form = CropForm(request.POST)
        if form.is_valid():
            crop = form.save(commit=False)
            crop.user = request.user
            crop.save()
            return redirect('/dashboard/')
    else:
        form = CropForm()

    return render(request, 'agriapp/add_crop.html', {'form': form})


@login_required
def my_crops(request):
    crops = Crop.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'agriapp/my_crops.html', {'crops': crops})


@login_required
def mandi_view(request):
    return render(request, "mandi.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return render(request, "register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, "register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(request, "register.html")

        User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        messages.success(request, "Account created successfully. Please login.")
        return redirect("/login/")

    return render(request, "register.html")


@login_required
def delete_crop(request, crop_id):
    crop = get_object_or_404(Crop, id=crop_id, user=request.user)
    crop.delete()
    return redirect('my_crops')


@login_required
def edit_crop(request, crop_id):
    crop = get_object_or_404(Crop, id=crop_id, user=request.user)

    if request.method == "POST":
        crop.name = request.POST.get("name")
        crop.season = request.POST.get("season")
        crop.area = request.POST.get("area")
        crop.save()
        return redirect('my_crops')

    return render(request, "edit_crop.html", {"crop": crop})