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

# NEW IMPORTS - Step 2-4
from .crop_weather_rules import get_crop_rules, get_season_rules, CROP_KNOWLEDGE_BASE
from .city_state_map import get_state_from_city
from .weather_forecast import get_7day_forecast, analyze_forecast_unpredictability, get_forecast_summary_en, get_forecast_summary_hi
from .state_risks import get_state_risk_advisories, get_risk_summary_en, get_risk_summary_hi

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
# DASHBOARD
# ========================================

@login_required
def dashboard(request):
    current_city = request.session.get('user_city', 'Delhi')
    user_crops = Crop.objects.filter(user=request.user).order_by('-created_at')
    weather_data = get_weather_data(current_city)
    
    crop_insights = []
    for crop in user_crops[:3]:
        insights = get_crop_weather_insights(crop.name, weather_data)
        crop_insights.append({
            'crop': crop,
            'insights': insights[:2]
        })
    
    farm_summary = generate_farm_summary(weather_data, user_crops)
    
    context = {
        'crops': user_crops,
        'weather': weather_data,
        'crop_insights': crop_insights,
        'farm_summary': farm_summary,
    }
    return render(request, "dashboard.html", context)

# ========================================
# ENHANCED WEATHER VIEW (STEP 2-4)
# ========================================

@login_required
def weather_view(request):
    city = request.GET.get('city')
    
    if city:
        request.session['user_city'] = city
    else:
        city = request.session.get('user_city', 'Delhi')
    
    # Get current weather
    weather_data = get_weather_data(city)
    user_crops = Crop.objects.filter(user=request.user)
    
    # Get state from city
    state = get_state_from_city(city)
    
    # Get 7-day forecast and analysis
    forecast_data = None
    forecast_analysis = None
    forecast_summary_en = None
    forecast_summary_hi = None
    
    if weather_data.get('lat') and weather_data.get('lon'):
        daily_forecasts = get_7day_forecast(weather_data['lat'], weather_data['lon'])
        if daily_forecasts:
            forecast_data = daily_forecasts
            forecast_analysis = analyze_forecast_unpredictability(daily_forecasts)
            if forecast_analysis:
                forecast_summary_en = get_forecast_summary_en(forecast_analysis)
                forecast_summary_hi = get_forecast_summary_hi(forecast_analysis)
    
    # Get state-based risk advisories
    state_risks = []
    state_risk_summary_en = None
    state_risk_summary_hi = None
    
    if state:
        state_risks = get_state_risk_advisories(state)
        state_risk_summary_en = get_risk_summary_en(state)
        state_risk_summary_hi = get_risk_summary_hi(state)
    
    # Get crop insights (existing logic)
    all_crop_insights = []
    for crop in user_crops:
        insights = get_crop_weather_insights(crop.name, weather_data, forecast_analysis)
        all_crop_insights.append({
            'crop': crop,
            'insights': insights
        })
    
    # Generate daily insights (existing logic)
    daily_insights = generate_daily_farm_insights(all_crop_insights, weather_data)
    
    context = {
        "city": weather_data['city'],
        "state": state if state else "Unknown Region",
        "temp": weather_data['temp'],
        "humidity": weather_data['humidity'],
        "description": weather_data['description'],
        "weather": weather_data,
        
        # 7-day forecast data
        "forecast_data": forecast_data,
        "forecast_analysis": forecast_analysis,
        "forecast_summary_en": forecast_summary_en,
        "forecast_summary_hi": forecast_summary_hi,
        
        # State risk data
        "state_risks": state_risks,
        "state_risk_summary_en": state_risk_summary_en,
        "state_risk_summary_hi": state_risk_summary_hi,
        
        # Existing data
        "all_crop_insights": all_crop_insights,
        "farm_summary": daily_insights['farm_summary'],
        "priority_actions": daily_insights['priority_actions'],
    }
    return render(request, "weather.html", context)

# ========================================
# WEATHER API HELPER (ENHANCED)
# ========================================

def get_weather_data(city="Delhi"):
    api_key = settings.OPENWEATHER_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if response.status_code != 200:
            raise Exception("City not found")
        
        return {
            'temp': round(data['main']['temp']),
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
            'city': city.title(),
            'lat': data['coord']['lat'],  # NEW - for forecast API
            'lon': data['coord']['lon']   # NEW - for forecast API
        }
    except:
        return {
            'temp': 25,
            'humidity': 60,
            'description': 'clear sky',
            'city': city.title(),
            'lat': None,
            'lon': None
        }

# ========================================
# OTHER VIEWS (UNCHANGED)
# ========================================

@login_required
def weather_api(request):
    city = request.GET.get('city')
    api_key = settings.OPENWEATHER_API_KEY
    if not city: return JsonResponse({"error": "City required"})
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    if response.status_code != 200: return JsonResponse({"error": "City not found"})
    return JsonResponse({
        "city": city, "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"], "description": data["weather"][0]["description"],
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
def delete_crop(request, crop_id):
    crop = get_object_or_404(Crop, id=crop_id, user=request.user)
    crop.delete()
    return redirect('my_crops')

@login_required
def edit_crop(request, crop_id):
    crop = get_object_or_404(Crop, id=crop_id, user=request.user)
    if request.method == "POST":
        crop.name = request.POST.get("name"); crop.season = request.POST.get("season")
        crop.area = request.POST.get("area"); crop.save()
        return redirect('my_crops')
    return render(request, "edit_crop.html", {"crop": crop})

# ========================================
# MANDI VIEW
# ========================================

VALID_COMMODITIES = ["Wheat", "Rice", "Potato", "Onion", "Tomato", "Cotton", "Mustard", "Maize", "Soyabean", "Gram", "Jowar", "Bajra", "Arhar (Tur)", "Moong", "Masur", "Groundnut", "Sunflower", "Apple", "Banana", "Mango", "Lemon","Sugarcane","Paddy"]
VALID_STATES = ["Andaman and Nicobar", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chandigarh", "Chattisgarh", "Dadra and Nagar Haveli", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Puducherry", "Punjab", "Rajasthan", "Sikkim", "kanpur", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"]

def smart_match(user_input, reference_list):
    if not user_input: return None
    user_input = user_input.strip().title()
    matches = get_close_matches(user_input, reference_list, n=1, cutoff=0.3)
    return matches[0] if matches else user_input

@login_required
def mandi_view(request):
    state_input = request.GET.get("state", ""); comm_input = request.GET.get("commodity", ""); dist_input = request.GET.get("district", "")
    final_state = smart_match(state_input, VALID_STATES); final_comm = smart_match(comm_input, VALID_COMMODITIES); final_dist = dist_input.strip().title() if dist_input else None
    params = {"api-key": settings.MANDI_API_KEY, "format": "json", "limit": 50}
    if final_state: params["filters[state.keyword]"] = final_state
    if final_comm: params["filters[commodity]"] = final_comm
    if final_dist: params["filters[district]"] = final_dist
    mandi_data = []; msg = ""; url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    try:
        response = requests.get(url, params=params); res_json = response.json(); mandi_data = res_json.get("records", [])
        if not mandi_data and final_dist:
            params["filters[district]"] = final_dist.upper(); res_upper = requests.get(url, params=params); mandi_data = res_upper.json().get("records", [])
        if not mandi_data and final_dist:
            del params["filters[district]"]; res_fallback = requests.get(url, params=params); mandi_data = res_fallback.json().get("records", [])
            if mandi_data: msg = f"'{final_dist}' me koi market nahi mila. Hum aapke state '{final_state}' ki baaki mandiyan dikha rahe hain."
        if not mandi_data and final_state:
            params = {"api-key": settings.MANDI_API_KEY, "format": "json", "limit": 20, "filters[state.keyword]": final_state}; res_state = requests.get(url, params=params); mandi_data = res_state.json().get("records", [])
            msg = f"'{final_comm}' ka rate abhi update nahi hua hai. Aapke state ki dusri fasalon ka rate dekhein."
    except Exception as e: msg = "Network me kuch problem hai, kripya thodi der baad koshish karein."
    return render(request, "mandi.html", {"mandi_data": mandi_data, "message": msg, "searched": {"state": final_state, "commodity": final_comm, "district": final_dist}, "valid_states": VALID_STATES, "valid_commodities": VALID_COMMODITIES})

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username"); email = request.POST.get("email"); p1 = request.POST.get("password1"); p2 = request.POST.get("password2")
        if p1 != p2: messages.error(request, "Passwords do not match"); return render(request, "register.html")
        if User.objects.filter(username=username).exists(): messages.error(request, "Username exists"); return render(request, "register.html")
        User.objects.create_user(username=username, email=email, password=p1)
        messages.success(request, "Account created successfully."); return redirect("/login/")
    return render(request, "register.html")

# ========================================
# ENHANCED CROP WEATHER INTELLIGENCE (STEP 4)
# ========================================

def get_crop_weather_insights(crop_name, weather_data, forecast_analysis=None):
    """
    Generate bilingual weather advisories for a specific crop
    Enhanced with 7-day forecast analysis
    """
    temp = weather_data['temp']
    humidity = weather_data['humidity']
    description = weather_data['description'].lower()
    
    insights = []
    crop_rules = get_crop_rules(crop_name)
    
    if crop_rules:
        crop_name_hi = crop_rules['crop_name_hi']
        ideal_min = crop_rules['ideal_temp_min']
        ideal_max = crop_rules['ideal_temp_max']
        heat_threshold = crop_rules['heat_stress_threshold']
        water_need = crop_rules['water_requirement']
        
        # === TEMPERATURE ANALYSIS (ENHANCED) ===
        
        # Check for extended heat stress from forecast
        extended_heat = False
        if forecast_analysis and forecast_analysis.get('max_consecutive_hot') >= 3:
            extended_heat = True
            insights.append({
                'advisory_key': 'EXTENDED_HEAT_STRESS',
                'message_en': f'⚠️ Extended heat period ({forecast_analysis["max_consecutive_hot"]} days) will stress {crop_name}',
                'message_hi': f'⚠️ लंबी गर्मी की अवधि ({forecast_analysis["max_consecutive_hot"]} दिन) {crop_name_hi} को तनाव देगी',
                'alert_type': 'danger',
                'suggested_action_en': f'Plan increased irrigation for next {forecast_analysis["max_consecutive_hot"]} days. Consider mulching to retain moisture.',
                'suggested_action_hi': f'अगले {forecast_analysis["max_consecutive_hot"]} दिनों के लिए बढ़ी हुई सिंचाई की योजना बनाएं। नमी बनाए रखने के लिए मल्चिंग पर विचार करें।',
                'icon': '🔥'
            })
        
        # Current day temperature stress
        if temp >= heat_threshold and not extended_heat:
            insights.append({
                'advisory_key': 'HEAT_STRESS_CRITICAL',
                'message_en': f'⚠️ Critical heat stress for {crop_name}',
                'message_hi': f'⚠️ {crop_name_hi} के लिए गंभीर गर्मी का तनाव',
                'alert_type': 'danger',
                'suggested_action_en': 'Irrigate early morning (before 7 AM). Provide shade if possible.',
                'suggested_action_hi': 'सुबह जल्दी (7 बजे से पहले) सिंचाई करें। संभव हो तो छाया दें।',
                'icon': '🔥'
            })
        elif temp > ideal_max:
            insights.append({
                'advisory_key': 'HEAT_STRESS_MODERATE',
                'message_en': f'High temperature may stress {crop_name}',
                'message_hi': f'अधिक तापमान {crop_name_hi} को नुकसान पहुँचा सकता है',
                'alert_type': 'warning',
                'suggested_action_en': 'Avoid irrigation during afternoon. Water in evening or early morning.',
                'suggested_action_hi': 'दोपहर में सिंचाई न करें। शाम या सुबह पानी दें।',
                'icon': '🌡️'
            })
        elif temp < ideal_min:
            insights.append({
                'advisory_key': 'COLD_STRESS',
                'message_en': f'Temperature below ideal for {crop_name}',
                'message_hi': f'{crop_name_hi} के लिए तापमान कम है',
                'alert_type': 'info',
                'suggested_action_en': 'Growth may slow down. No immediate action needed.',
                'suggested_action_hi': 'विकास धीमा हो सकता है। तुरंत कोई कार्रवाई जरूरी नहीं।',
                'icon': '❄️'
            })
        else:
            insights.append({
                'advisory_key': 'TEMP_FAVORABLE',
                'message_en': f'Favorable temperature for {crop_name}',
                'message_hi': f'{crop_name_hi} के लिए अनुकूल तापमान',
                'alert_type': 'success',
                'suggested_action_en': 'Continue normal farming practices.',
                'suggested_action_hi': 'सामान्य खेती जारी रखें।',
                'icon': '✅'
            })
        
        # === UNPREDICTABILITY WARNING ===
        
        if forecast_analysis and forecast_analysis.get('stability_score') == 'HIGHLY UNSTABLE':
            insights.append({
                'advisory_key': 'WEATHER_UNPREDICTABLE',
                'message_en': f'Unstable weather pattern this week - risky for {crop_name}',
                'message_hi': f'इस सप्ताह अस्थिर मौसम पैटर्न - {crop_name_hi} के लिए जोखिम भरा',
                'alert_type': 'warning',
                'suggested_action_en': 'Delay major farming decisions (spraying, fertilizing). Monitor daily weather.',
                'suggested_action_hi': 'प्रमुख खेती के निर्णयों (छिड़काव, उर्वरक) में देरी करें। दैनिक मौसम की निगरानी करें।',
                'icon': '⚠️'
            })
        
        # === IRRIGATION ANALYSIS ===
        
        if 'rain' in description or 'drizzle' in description:
            insights.append({
                'advisory_key': 'RAIN_DETECTED',
                'message_en': 'Rain expected or ongoing',
                'message_hi': 'बारिश होने वाली है या हो रही है',
                'alert_type': 'info',
                'suggested_action_en': 'Skip irrigation today. Save water and costs.',
                'suggested_action_hi': 'आज सिंचाई छोड़ दें। पानी और खर्च बचाएं।',
                'icon': '🌧️'
            })
        else:
            if water_need == 'HIGH' and humidity < 60:
                insights.append({
                    'advisory_key': 'IRRIGATION_HIGH_NEED',
                    'message_en': f'{crop_name} needs regular watering',
                    'message_hi': f'{crop_name_hi} को नियमित पानी चाहिए',
                    'alert_type': 'warning',
                    'suggested_action_en': 'Irrigate daily. Check soil moisture regularly.',
                    'suggested_action_hi': 'रोज़ाना सिंचाई करें। मिट्टी की नमी जांचें।',
                    'icon': '💧'
                })
            elif water_need == 'MEDIUM' and humidity < 50 and temp > 30:
                insights.append({
                    'advisory_key': 'IRRIGATION_MEDIUM_NEED',
                    'message_en': 'Moderate irrigation required',
                    'message_hi': 'मध्यम सिंचाई आवश्यक है',
                    'alert_type': 'info',
                    'suggested_action_en': 'Irrigate every 2-3 days based on soil condition.',
                    'suggested_action_hi': 'मिट्टी की स्थिति के अनुसार 2-3 दिन में सिंचाई करें।',
                    'icon': '💧'
                })
            elif water_need == 'LOW' and temp > 35:
                insights.append({
                    'advisory_key': 'IRRIGATION_LOW_NEED',
                    'message_en': f'{crop_name} is drought-tolerant but needs care in heat',
                    'message_hi': f'{crop_name_hi} सूखा सहनशील है पर गर्मी में देखभाल चाहिए',
                    'alert_type': 'info',
                    'suggested_action_en': 'Light irrigation every 4-5 days is sufficient.',
                    'suggested_action_hi': 'हर 4-5 दिन में हल्की सिंचाई काफी है।',
                    'icon': '💧'
                })
        
        # === DISEASE RISK ===
        
        if humidity > 80:
            insights.append({
                'advisory_key': 'FUNGAL_RISK',
                'message_en': 'High humidity increases fungal disease risk',
                'message_hi': 'अधिक नमी से फफूंद रोग का खतरा बढ़ता है',
                'alert_type': 'warning',
                'suggested_action_en': 'Monitor for leaf spots. Ensure good air circulation.',
                'suggested_action_hi': 'पत्तियों पर धब्बे देखें। हवा का संचार अच्छा रखें।',
                'icon': '🍄'
            })
    
    else:
        # Fallback for unknown crops
        if temp > 35:
            insights.append({
                'advisory_key': 'GENERIC_HEAT',
                'message_en': f'High heat may affect {crop_name}',
                'message_hi': f'अधिक गर्मी {crop_name} को प्रभावित कर सकती है',
                'alert_type': 'warning',
                'suggested_action_en': 'Increase watering frequency. Avoid midday activities.',
                'suggested_action_hi': 'पानी देने की आवृत्ति बढ़ाएं। दोपहर में काम न करें।',
                'icon': '🔥'
            })
        elif temp < 15:
            insights.append({
                'advisory_key': 'GENERIC_COLD',
                'message_en': f'Cool weather for {crop_name}',
                'message_hi': f'{crop_name} के लिए ठंडा मौसम',
                'alert_type': 'info',
                'suggested_action_en': 'Monitor growth. Protect from frost if needed.',
                'suggested_action_hi': 'विकास पर नजर रखें। जरूरत हो तो पाले से बचाएं।',
                'icon': '❄️'
            })
        else:
            insights.append({
                'advisory_key': 'GENERIC_NORMAL',
                'message_en': f'Weather conditions suitable for {crop_name}',
                'message_hi': f'{crop_name} के लिए मौसम उपयुक्त है',
                'alert_type': 'success',
                'suggested_action_en': 'Continue regular farm operations.',
                'suggested_action_hi': 'नियमित खेती जारी रखें।',
                'icon': '✅'
            })
        
        if 'rain' in description:
            insights.append({
                'advisory_key': 'GENERIC_RAIN',
                'message_en': 'Rain expected',
                'message_hi': 'बारिश की संभावना',
                'alert_type': 'info',
                'suggested_action_en': 'Skip irrigation. Prepare drainage if heavy rain.',
                'suggested_action_hi': 'सिंचाई छोड़ें। भारी बारिश हो तो जल निकासी तैयार रखें।',
                'icon': '🌧️'
            })
    
    return insights

def generate_farm_summary(weather_data, crops):
    temp = weather_data['temp']; hum = weather_data['humidity']; desc = weather_data['description'].lower()
    summary = []
    if temp > 35: summary.append('🔥 Heat Alert: Monitor all crops.')
    if 'rain' in desc: summary.append('🌧️ Rain Expected: Hold irrigation.')
    if not summary: summary.append('✅ Normal conditions today.')
    return summary[:3]

# ========================================
# DAILY FARM INSIGHTS
# ========================================

def generate_daily_farm_insights(all_crop_insights, weather_data):
    temp = weather_data['temp']
    humidity = weather_data['humidity']
    description = weather_data['description'].lower()
    
    crops_under_stress = 0
    crops_needing_monitoring = 0
    crops_doing_well = 0
    priority_actions = []
    
    for item in all_crop_insights:
        crop = item['crop']
        insights = item['insights']
        
        has_danger = False
        has_warning = False
        
        for insight in insights:
            alert_type = insight.get('alert_type', 'info')
            
            if alert_type == 'danger':
                has_danger = True
                priority_actions.append({
                    'priority': 1,
                    'crop': crop.name,
                    'crop_area': crop.area,
                    'action_en': insight['suggested_action_en'],
                    'action_hi': insight['suggested_action_hi'],
                    'urgency': 'high',
                    'icon': insight.get('icon', '⚠️')
                })
            elif alert_type == 'warning':
                has_warning = True
                priority_actions.append({
                    'priority': 2,
                    'crop': crop.name,
                    'crop_area': crop.area,
                    'action_en': insight['suggested_action_en'],
                    'action_hi': insight['suggested_action_hi'],
                    'urgency': 'medium',
                    'icon': insight.get('icon', '💡')
                })
        
        if has_danger:
            crops_under_stress += 1
        elif has_warning:
            crops_needing_monitoring += 1
        else:
            crops_doing_well += 1
            if insights:
                priority_actions.append({
                    'priority': 3,
                    'crop': crop.name,
                    'crop_area': crop.area,
                    'action_en': insights[0]['suggested_action_en'],
                    'action_hi': insights[0]['suggested_action_hi'],
                    'urgency': 'low',
                    'icon': insights[0].get('icon', '✅')
                })
    
    priority_actions.sort(key=lambda x: x['priority'])
    
    primary_action = 'NORMAL'
    primary_action_en = 'Continue regular farm operations'
    primary_action_hi = 'नियमित खेती जारी रखें'
    weather_tip_en = 'Weather conditions are stable today.'
    weather_tip_hi = 'मौसम की स्थिति आज स्थिर है।'
    
    if temp > 35:
        primary_action = 'IRRIGATE'
        primary_action_en = 'Focus on irrigation today'
        primary_action_hi = 'आज सिंचाई पर ध्यान दें'
        weather_tip_en = f'High temperature ({temp}°C) - water crops early morning (before 7 AM).'
        weather_tip_hi = f'उच्च तापमान ({temp}°C) - सुबह जल्दी (7 बजे से पहले) फसलों को पानी दें।'
    elif humidity > 80:
        primary_action = 'MONITOR'
        primary_action_en = 'Monitor crops for disease'
        primary_action_hi = 'फसलों में बीमारी की निगरानी करें'
        weather_tip_en = f'High humidity ({humidity}%) increases fungal disease risk.'
        weather_tip_hi = f'अधिक नमी ({humidity}%) से फफूंद रोग का खतरा बढ़ता है।'
    elif 'rain' in description:
        primary_action = 'PROTECT'
        primary_action_en = 'Prepare for rain'
        primary_action_hi = 'बारिश के लिए तैयार रहें'
        weather_tip_en = 'Rain expected - skip irrigation and ensure drainage.'
        weather_tip_hi = 'बारिश की संभावना - सिंचाई छोड़ें।'
    elif temp < 15:
        primary_action = 'PROTECT'
        primary_action_en = 'Protect from cold'
        primary_action_hi = 'ठंड से बचाएं'
        weather_tip_en = f'Low temperature ({temp}°C) - protect from frost.'
        weather_tip_hi = f'कम तापमान ({temp}°C) - पाले से बचाएं।'
    elif crops_under_stress > 0:
        primary_action = 'URGENT_ACTION'
        primary_action_en = 'Urgent action required'
        primary_action_hi = 'तत्काल कार्रवाई आवश्यक'
        weather_tip_en = f'{crops_under_stress} crop(s) under stress.'
        weather_tip_hi = f'{crops_under_stress} फसल(ें) तनाव में हैं।'
    
    farm_summary = {
        'primary_action': primary_action,
        'primary_action_en': primary_action_en,
        'primary_action_hi': primary_action_hi,
        'crops_under_stress': crops_under_stress,
        'crops_needing_monitoring': crops_needing_monitoring,
        'crops_doing_well': crops_doing_well,
        'total_crops': len(all_crop_insights),
        'weather_tip_en': weather_tip_en,
        'weather_tip_hi': weather_tip_hi,
        'temp': temp,
        'humidity': humidity
    }
    
    return {
        'farm_summary': farm_summary,
        'priority_actions': priority_actions[:5]
    }

@login_required
def crop_insight_api(request, crop_name):
    city = request.session.get('user_city', 'Delhi')
    weather_data = get_weather_data(city)
    insights = get_crop_weather_insights(crop_name, weather_data)
    return JsonResponse({'crop': crop_name, 'insights': insights})