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
from difflib import get_close_matches

# ========================================
# EXISTING VIEWS (UNTOUCHED)
# ========================================

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

def logout_view(request):
    logout(request)
    return redirect('/')


# ========================================
# MODIFIED DASHBOARD (ENHANCED WITH WEATHER)
# ========================================

@login_required
def dashboard(request):
    """
    Enhanced dashboard with weather-crop integration
    """
    # Get user's crops
    user_crops = Crop.objects.filter(user=request.user).order_by('-created_at')
    
    # Get weather data
    weather_data = get_weather_data()
    
    # Generate crop-specific insights (top 3 crops for dashboard)
    crop_insights = []
    for crop in user_crops[:3]:
        insights = get_crop_weather_insights(crop.name, weather_data)
        crop_insights.append({
            'crop': crop,
            'insights': insights[:2]  # Show top 2 insights per crop on dashboard
        })
    
    # Generate farm-wide summary
    farm_summary = generate_farm_summary(weather_data, user_crops)
    
    context = {
        'crops': user_crops,
        'weather': weather_data,
        'crop_insights': crop_insights,
        'farm_summary': farm_summary,
    }
    
    return render(request, "dashboard.html", context)


# ========================================
# MODIFIED WEATHER VIEW (DETAILED ANALYSIS)
# ========================================

@login_required
def weather_view(request):
    """
    Detailed weather analysis page with all crops
    """
    city = request.GET.get('city', 'Delhi')
    api_key = settings.OPENWEATHER_API_KEY

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=metric"
    )

    try:
        response = requests.get(url)
        data = response.json()
        
        weather_data = {
            "city": city,
            "temp": round(data.get("main", {}).get("temp", 25)),
            "humidity": data.get("main", {}).get("humidity", 60),
            "description": data.get("weather", [{}])[0].get("description", "clear sky"),
        }
    except:
        # Fallback data if API fails
        weather_data = {
            "city": city,
            "temp": 25,
            "humidity": 60,
            "description": "clear sky",
        }
    
    # Get all user crops with insights
    user_crops = Crop.objects.filter(user=request.user)
    all_crop_insights = []
    
    for crop in user_crops:
        insights = get_crop_weather_insights(crop.name, weather_data)
        all_crop_insights.append({
            'crop': crop,
            'insights': insights
        })
    
    context = {
        "city": weather_data['city'],
        "temp": weather_data['temp'],
        "humidity": weather_data['humidity'],
        "description": weather_data['description'],
        "weather": weather_data,
        "all_crop_insights": all_crop_insights,
    }

    return render(request, "weather.html", context)


# ========================================
# EXISTING WEATHER API (UNTOUCHED)
# ========================================

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


# ========================================
# CROP MANAGEMENT (UNTOUCHED)
# ========================================

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


# ========================================
# MANDI PRICE VIEW (UNTOUCHED)
# ========================================

VALID_COMMODITIES = [
    "Wheat", "Rice", "Potato", "Onion", "Tomato", "Cotton", "Mustard", "Maize", 
    "Soyabean", "Gram", "Jowar", "Bajra", "Arhar (Tur)", "Moong", "Masur", 
    "Groundnut", "Sunflower", "Apple", "Banana", "Mango", "Lemon","Sugarcane","Paddy"
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

        if not mandi_data and final_dist:
            params["filters[district]"] = final_dist.upper()
            res_upper = requests.get(url, params=params)
            mandi_data = res_upper.json().get("records", [])

        if not mandi_data and final_dist:
            del params["filters[district]"]
            res_fallback = requests.get(url, params=params)
            mandi_data = res_fallback.json().get("records", [])
            if mandi_data:
                msg = f"'{final_dist}' me koi market nahi mila. Hum aapke state '{final_state}' ki baaki mandiyan dikha rahe hain."
       
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


# ========================================
# REGISTER VIEW (UNTOUCHED)
# ========================================

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


# ========================================
# ✨ NEW HELPER FUNCTIONS (WEATHER INTELLIGENCE)
# ========================================

def get_weather_data(city="Delhi"):
    """
    Fetch current weather from OpenWeather API
    """
    api_key = settings.OPENWEATHER_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        return {
            'temp': round(data['main']['temp']),
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
            'city': city
        }
    except:
        # Fallback data if API fails
        return {
            'temp': 25,
            'humidity': 60,
            'description': 'clear sky',
            'city': city
        }


def get_crop_weather_insights(crop_name, weather_data):
    """
    Convert raw weather into farmer-friendly, crop-specific insights
    """
    temp = weather_data['temp']
    humidity = weather_data['humidity']
    description = weather_data['description'].lower()
    
    # ✅ CROP PROFILES - Easily expandable
    crop_profiles = {
        'wheat': {'ideal_temp': (15, 25), 'ideal_humidity': (50, 70)},
        'rice': {'ideal_temp': (20, 35), 'ideal_humidity': (60, 80)},
        'paddy': {'ideal_temp': (20, 35), 'ideal_humidity': (60, 80)},
        'tomato': {'ideal_temp': (18, 27), 'ideal_humidity': (60, 85)},
        'corn': {'ideal_temp': (18, 32), 'ideal_humidity': (50, 75)},
        'maize': {'ideal_temp': (18, 32), 'ideal_humidity': (50, 75)},
        'potato': {'ideal_temp': (15, 20), 'ideal_humidity': (60, 80)},
        'sugarcane': {'ideal_temp': (20, 30), 'ideal_humidity': (70, 90)},
        'cotton': {'ideal_temp': (21, 30), 'ideal_humidity': (50, 80)},
        'onion': {'ideal_temp': (13, 24), 'ideal_humidity': (50, 70)},
        'soyabean': {'ideal_temp': (20, 30), 'ideal_humidity': (60, 80)},
        'mustard': {'ideal_temp': (10, 25), 'ideal_humidity': (50, 70)},
        'gram': {'ideal_temp': (20, 30), 'ideal_humidity': (50, 70)},
        'groundnut': {'ideal_temp': (20, 30), 'ideal_humidity': (50, 70)},
        'jowar': {'ideal_temp': (25, 32), 'ideal_humidity': (50, 70)},
        'bajra': {'ideal_temp': (25, 35), 'ideal_humidity': (40, 60)},
        'arhar': {'ideal_temp': (20, 30), 'ideal_humidity': (50, 70)},
        'tur': {'ideal_temp': (20, 30), 'ideal_humidity': (50, 70)},
        'moong': {'ideal_temp': (25, 35), 'ideal_humidity': (60, 80)},
        'masur': {'ideal_temp': (18, 25), 'ideal_humidity': (50, 70)},
        'sunflower': {'ideal_temp': (20, 30), 'ideal_humidity': (50, 70)},
        'apple': {'ideal_temp': (15, 25), 'ideal_humidity': (60, 75)},
        'banana': {'ideal_temp': (25, 35), 'ideal_humidity': (75, 85)},
        'mango': {'ideal_temp': (24, 30), 'ideal_humidity': (50, 70)},
        'lemon': {'ideal_temp': (20, 30), 'ideal_humidity': (60, 75)},
    }
    
    crop_lower = crop_name.lower().strip()
    is_known_crop = crop_lower in crop_profiles
    
    # ✅ DEFAULT FALLBACK - No crashes for unknown crops
    profile = crop_profiles.get(crop_lower, {
        'ideal_temp': (20, 30), 
        'ideal_humidity': (50, 70)
    })
    
    insights = []
    
    # ✅ SMART MESSAGE - Show if using defaults
    if not is_known_crop:
        insights.append({
            'type': 'info',
            'icon': 'ℹ️',
            'message': f'Using general weather guidelines for {crop_name}',
            'action': 'Specific crop profile can be added for better accuracy'
        })
    
    # 🌡️ TEMPERATURE ANALYSIS
    if temp > profile['ideal_temp'][1] + 5:
        insights.append({
            'type': 'danger',
            'icon': '🔥',
            'message': f'High heat stress risk for {crop_name}',
            'action': 'Increase irrigation frequency. Water in early morning or evening'
        })
    elif temp > profile['ideal_temp'][1]:
        insights.append({
            'type': 'warning',
            'icon': '⚠️',
            'message': f'Temperature above ideal range for {crop_name}',
            'action': 'Ensure adequate watering and monitor plant health'
        })
    elif temp < profile['ideal_temp'][0]:
        insights.append({
            'type': 'info',
            'icon': '❄️',
            'message': f'Cool conditions for {crop_name}',
            'action': 'Growth may slow. Reduce irrigation frequency'
        })
    else:
        insights.append({
            'type': 'success',
            'icon': '✅',
            'message': f'Favorable temperature conditions for {crop_name}',
            'action': 'Continue normal care routine'
        })
    
    # 💧 HUMIDITY ANALYSIS
    if humidity < profile['ideal_humidity'][0]:
        insights.append({
            'type': 'warning',
            'icon': '💧',
            'message': 'Low humidity - dry conditions',
            'action': 'Increase irrigation frequency and check soil moisture regularly'
        })
    elif humidity > profile['ideal_humidity'][1]:
        insights.append({
            'type': 'warning',
            'icon': '🌫️',
            'message': 'High humidity - disease risk increased',
            'action': 'Monitor for fungal diseases. Ensure good air circulation'
        })
    
    # 🌧️ WEATHER CONDITION ANALYSIS
    if 'rain' in description:
        insights.append({
            'type': 'info',
            'icon': '🌧️',
            'message': 'Rainfall expected today',
            'action': 'Skip irrigation. Check field drainage systems'
        })
    
    return insights


def generate_farm_summary(weather_data, crops):
    """
    Generate 2-3 key alerts for the entire farm
    """
    temp = weather_data['temp']
    humidity = weather_data['humidity']
    description = weather_data['description'].lower()
    
    summary = []
    
    # Temperature alerts
    if temp > 35:
        summary.append('🔥 Heat Alert: High temperatures today. All crops need close monitoring.')
    elif temp < 10:
        summary.append('❄️ Cold Alert: Protect sensitive crops from potential frost damage.')
    
    # Humidity alerts
    if humidity < 40:
        summary.append('💧 Dry Conditions: Consider increasing irrigation across all fields.')
    elif humidity > 80:
        summary.append('🌫️ High Humidity: Watch for fungal diseases in all crops.')
    
    # Weather condition alerts
    if 'rain' in description:
        summary.append('🌧️ Rain Expected: Hold off on irrigation and fertilizer application today.')
    
    # Default positive message
    if not summary:
        summary.append('✅ Favorable Conditions: Normal farm operations recommended today.')
    
    return summary[:3]  # Return maximum 3 alerts


# ========================================
# ✨ NEW API ENDPOINT (for AJAX refresh)
# ========================================

@login_required
def crop_insight_api(request, crop_name):
    """
    API endpoint for dynamic insight refresh via JavaScript
    """
    weather_data = get_weather_data()
    insights = get_crop_weather_insights(crop_name, weather_data)
    
    return JsonResponse({
        'crop': crop_name,
        'insights': insights
    })