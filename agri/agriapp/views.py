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
    return redirect('/')

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


import requests
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from difflib import get_close_matches

VALID_COMMODITIES = [
    "Wheat", "Rice", "Potato", "Onion", "Tomato", "Cotton", "Mustard", "Maize", 
    "Soyabean", "Gram", "Jowar", "Bajra", "Arhar (Tur)", "Moong", "Masur", 
    "Groundnut", "Sunflower", "Apple", "Banana", "Mango", "Lemon","Sugarcane","paddy"
]

VALID_STATES = [
    "Andaman and Nicobar", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", 
    "Chandigarh", "Chattisgarh", "Dadra and Nagar Haveli", "Goa", "Gujarat", 
    "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand", "Karnataka", 
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", 
    "Nagaland", "Odisha", "Puducherry", "Punjab", "Rajasthan", "Sikkim", "kanpur",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
]

def smart_match(user_input, reference_list):
    if not user_input:
        return None
    user_input = user_input.strip().title()
    matches = get_close_matches(user_input, reference_list, n=1, cutoff=0.3)
    return matches[0] if matches else user_input

@login_required

def mandi_view(request):

    state_input = request.GET.get("state", "")

    comm_input = request.GET.get("commodity", "")

    dist_input = request.GET.get("district", "")



    final_state = smart_match(state_input, VALID_STATES)

    final_comm = smart_match(comm_input, VALID_COMMODITIES)

   

    # District ko Title Case mein rakha

    final_dist = dist_input.strip().title() if dist_input else None



    params = {

        "api-key": settings.MANDI_API_KEY,

        "format": "json",

        "limit": 50

    }



    if final_state: params["filters[state.keyword]"] = final_state

    if final_comm: params["filters[commodity]"] = final_comm

    if final_dist: params["filters[district]"] = final_dist



    mandi_data = []

    msg = ""

    url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"



    try:

        response = requests.get(url, params=params)

        res_json = response.json()

        mandi_data = res_json.get("records", [])



        # --- SMART LOGIC: Agar Title Case (Ghaziabad) se nahi mila ---

        if not mandi_data and final_dist:

            # ALL CAPS try karte hain (GHAZIABAD) kyunki API kabhi ye mangti hai

            params["filters[district]"] = final_dist.upper()

            res_upper = requests.get(url, params=params)

            mandi_data = res_upper.json().get("records", [])



        # --- FALLBACK: Agar District mein data hai hi nahi ---

        if not mandi_data and final_dist:

            # District filter hata kar poore State ka search

            del params["filters[district]"]

            res_fallback = requests.get(url, params=params)

            mandi_data = res_fallback.json().get("records", [])

            if mandi_data:

                msg = f"'{final_dist}' me koi market nahi mila. Hum aapke state '{final_state}' ki baaki mandiyan dikha rahe hain."

       

        # --- EXTREME FALLBACK: Agar Commodity bhi nahi mili us state mein ---

        if not mandi_data and final_state:

            params = {"api-key": settings.MANDI_API_KEY, "format": "json", "limit": 20, "filters[state.keyword]": final_state}

            res_state = requests.get(url, params=params)

            mandi_data = res_state.json().get("records", [])

            msg = f"'{final_comm}' ka rate abhi update nahi hua hai. Aapke state ki dusri fasalon ka rate dekhein."



    except Exception as e:

        msg = "Network me kuch problem hai, kripya thodi der baad koshish karein."



    return render(request, "mandi.html", {

        "mandi_data": mandi_data,

        "message": msg,

        "searched": {"state": final_state, "commodity": final_comm, "district": final_dist},
        "valid_states": VALID_STATES,
        "valid_commodities": VALID_COMMODITIES,
})
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