# agriapp/utils.py

CLIMATE_ZONE_MAP = {
    "chennai": "coastal",
    "mumbai": "coastal",
    "kolkata": "coastal",

    "delhi": "inland",
    "lucknow": "inland",
    "kanpur": "inland",

    "jaipur": "arid",
    "jodhpur": "arid",
    "bikaner": "arid",
}

CLIMATE_WATER_FACTOR = {
    "coastal": 0.85,
    "inland": 1.0,
    "arid": 1.25,
}

CLIMATE_UREA_FACTOR = {
    "coastal": 0.9,
    "inland": 1.0,
    "arid": 1.1,
}


def apply_location_adjustment(base_water, base_urea, place_name):
    """
    Adjust water and urea based on location climate zone
    (PURE FUNCTION — no request, no session)
    """
    if not place_name:
        return base_water, base_urea

    zone = CLIMATE_ZONE_MAP.get(place_name.lower(), "inland")

    adjusted_water = base_water * CLIMATE_WATER_FACTOR[zone]
    adjusted_urea = base_urea * CLIMATE_UREA_FACTOR[zone]

    return round(adjusted_water, 2), round(adjusted_urea, 2)




def generate_daily_farm_insights(all_crop_insights, weather_data):
    """
    Generate farm-wide summary and priority actions
    Analyzes all crop advisories to determine today's farming priorities
    """
      
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


def generate_farm_summary(weather_data, user_crops):
    """
    Generates high-level farm dashboard summary
    """
    temp = weather_data.get("temp")
    humidity = weather_data.get("humidity")

    total_crops = user_crops.count()

    status = "NORMAL"
    advice_en = "Farm conditions are stable."
    advice_hi = "खेत की स्थिति सामान्य है।"

    if temp and temp > 35:
        status = "HOT"
        advice_en = "High temperature – irrigation needed."
        advice_hi = "अधिक तापमान – सिंचाई आवश्यक है।"
    elif humidity and humidity > 80:
        status = "HUMID"
        advice_en = "High humidity – monitor for disease."
        advice_hi = "अधिक नमी – रोगों पर नजर रखें।"

    # Return statement missing in your code - adding it
    return {
        'status': status,
        'advice_en': advice_en,
        'advice_hi': advice_hi,
        'total_crops': total_crops,
        'temp': temp,
        'humidity': humidity
    }


# ============================================
# NEW FUNCTIONS TO ADD (CROP RULES & IMD THRESHOLDS)
# ============================================

def get_crop_rules(crop_name):
    """
    Simple crop rules for temperature thresholds
    Works for ANY crop - unlimited
    """
    if not crop_name:
        return {
            "season": "General",
            "water_requirement": "MEDIUM",
            "heat_stress": 35,
            "cold_stress": 10
        }
    
    crop_lower = crop_name.lower()
    
    # Simple detection - unlimited crops
    if "rice" in crop_lower:
        return {"heat_stress": 38, "cold_stress": 15, "season": "Kharif/Rabi"}
    elif "wheat" in crop_lower:
        return {"heat_stress": 30, "cold_stress": 10, "season": "Rabi"}
    elif "potato" in crop_lower:
        return {"heat_stress": 30, "cold_stress": 8, "season": "Rabi"}
    elif "tomato" in crop_lower:
        return {"heat_stress": 32, "cold_stress": 10, "season": "All"}
    elif "cotton" in crop_lower:
        return {"heat_stress": 38, "cold_stress": 15, "season": "Kharif"}
    elif "maize" in crop_lower or "corn" in crop_lower:
        return {"heat_stress": 35, "cold_stress": 12, "season": "Kharif"}
    elif "sugarcane" in crop_lower:
        return {"heat_stress": 38, "cold_stress": 15, "season": "Year-round"}
    elif "gram" in crop_lower or "chana" in crop_lower:
        return {"heat_stress": 35, "cold_stress": 10, "season": "Rabi"}
    elif "mustard" in crop_lower or "sarson" in crop_lower:
        return {"heat_stress": 30, "cold_stress": 8, "season": "Rabi"}
    else:
        # Default for any unknown crop
        return {"heat_stress": 35, "cold_stress": 10, "season": "General"}


# Simple IMD thresholds
IMD_THRESHOLDS = {
    "heat_wave": 40,
    "cold_wave": 10
}

   