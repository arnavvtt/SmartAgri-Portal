"""
7-Day Weather Forecast Analysis
Calculates unpredictability, stability score, and multi-day trends
Uses OpenWeather One Call API 3.0 (free tier)
"""

import requests
from django.conf import settings


def get_7day_forecast(lat, lon):
    """
    Fetch 7-day forecast from OpenWeather One Call API
    Free tier allows 1000 calls/day
    """
    api_key = settings.OPENWEATHER_API_KEY
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if response.status_code != 200:
            return None
        
        # Extract daily data (API gives 3-hour intervals, we'll aggregate to daily)
        daily_forecasts = []
        current_date = None
        day_temps = []
        day_humidity = []
        day_rain = 0
        
        for item in data['list'][:40]:  # Next 5 days (8 readings per day)
            date = item['dt_txt'].split(' ')[0]
            
            if current_date is None:
                current_date = date
            
            if date != current_date:
                # New day started, aggregate previous day
                if day_temps:
                    daily_forecasts.append({
                        'date': current_date,
                        'temp_max': round(max(day_temps)),
                        'temp_min': round(min(day_temps)),
                        'temp_avg': round(sum(day_temps) / len(day_temps)),
                        'humidity_avg': round(sum(day_humidity) / len(day_humidity)),
                        'rain_probability': day_rain > 0,
                        'description': item['weather'][0]['description']
                    })
                
                # Reset for new day
                current_date = date
                day_temps = []
                day_humidity = []
                day_rain = 0
            
            # Collect data for current day
            day_temps.append(item['main']['temp'])
            day_humidity.append(item['main']['humidity'])
            if 'rain' in item:
                day_rain = 1
        
        return daily_forecasts[:7]  # Return max 7 days
    
    except Exception as e:
        print(f"Forecast API Error: {e}")
        return None


def analyze_forecast_unpredictability(daily_forecasts):
    """
    Analyze 7-day forecast for:
    - Temperature fluctuations (sudden changes ≥ 6°C)
    - Consecutive hot days (≥ 38°C)
    - Rain pattern inconsistency
    - Overall stability score
    """
    if not daily_forecasts or len(daily_forecasts) < 3:
        return None
    
    analysis = {
        'fluctuation_count': 0,
        'fluctuation_days': [],
        'consecutive_hot_days': 0,
        'max_consecutive_hot': 0,
        'rain_days': 0,
        'temp_range': 0,
        'stability_score': 'STABLE',
        'stability_color': 'success',
        'risk_level': 'LOW',
        'warnings': []
    }
    
    temps = [day['temp_max'] for day in daily_forecasts]
    analysis['temp_range'] = max(temps) - min(temps)
    
    # 1. Temperature Fluctuation Analysis
    for i in range(len(daily_forecasts) - 1):
        temp_diff = abs(daily_forecasts[i+1]['temp_max'] - daily_forecasts[i]['temp_max'])
        if temp_diff >= 6:
            analysis['fluctuation_count'] += 1
            analysis['fluctuation_days'].append({
                'day': i+1,
                'change': round(temp_diff, 1)
            })
    
    # 2. Consecutive Hot Days (≥ 38°C)
    current_streak = 0
    for day in daily_forecasts:
        if day['temp_max'] >= 38:
            current_streak += 1
            analysis['consecutive_hot_days'] = current_streak
            analysis['max_consecutive_hot'] = max(analysis['max_consecutive_hot'], current_streak)
        else:
            current_streak = 0
    
    # 3. Rain Pattern
    for day in daily_forecasts:
        if day['rain_probability']:
            analysis['rain_days'] += 1
    
    # 4. Stability Scoring
    instability_points = 0
    
    # Large temp range (>15°C across week)
    if analysis['temp_range'] > 15:
        instability_points += 2
        analysis['warnings'].append('Wide temperature variation this week')
    
    # Multiple fluctuations (≥3 sudden changes)
    if analysis['fluctuation_count'] >= 3:
        instability_points += 3
        analysis['warnings'].append(f'{analysis["fluctuation_count"]} sudden temperature changes expected')
    elif analysis['fluctuation_count'] >= 1:
        instability_points += 1
    
    # Extended heat stress
    if analysis['max_consecutive_hot'] >= 3:
        instability_points += 2
        analysis['warnings'].append(f'{analysis["max_consecutive_hot"]} consecutive days above 38°C')
    
    # Intermittent rain (unpredictable irrigation)
    if 1 <= analysis['rain_days'] <= 3:
        instability_points += 1
        analysis['warnings'].append('Intermittent rain expected - irrigation planning difficult')
    
    # Final Stability Assessment
    if instability_points >= 5:
        analysis['stability_score'] = 'HIGHLY UNSTABLE'
        analysis['stability_color'] = 'danger'
        analysis['risk_level'] = 'HIGH'
    elif instability_points >= 3:
        analysis['stability_score'] = 'MODERATELY UNSTABLE'
        analysis['stability_color'] = 'warning'
        analysis['risk_level'] = 'MEDIUM'
    else:
        analysis['stability_score'] = 'STABLE'
        analysis['stability_color'] = 'success'
        analysis['risk_level'] = 'LOW'
    
    return analysis


def get_forecast_summary_en(analysis):
    """Generate English summary of forecast analysis"""
    if not analysis:
        return "Forecast data unavailable"
    
    summary = f"Weather pattern: {analysis['stability_score']}. "
    
    if analysis['fluctuation_count'] > 0:
        summary += f"Expect {analysis['fluctuation_count']} sudden temperature changes. "
    
    if analysis['max_consecutive_hot'] >= 2:
        summary += f"Extended heat period of {analysis['max_consecutive_hot']} days. "
    
    if analysis['rain_days'] > 0:
        summary += f"Rain expected on {analysis['rain_days']} days. "
    
    return summary.strip()


def get_forecast_summary_hi(analysis):
    """Generate Hindi summary of forecast analysis"""
    if not analysis:
        return "पूर्वानुमान डेटा उपलब्ध नहीं"
    
    stability_map = {
        'STABLE': 'स्थिर',
        'MODERATELY UNSTABLE': 'मध्यम अस्थिर',
        'HIGHLY UNSTABLE': 'अत्यधिक अस्थिर'
    }
    
    summary = f"मौसम पैटर्न: {stability_map[analysis['stability_score']]}। "
    
    if analysis['fluctuation_count'] > 0:
        summary += f"{analysis['fluctuation_count']} अचानक तापमान परिवर्तन की उम्मीद। "
    
    if analysis['max_consecutive_hot'] >= 2:
        summary += f"{analysis['max_consecutive_hot']} दिनों तक गर्मी की अवधि। "
    
    if analysis['rain_days'] > 0:
        summary += f"{analysis['rain_days']} दिन बारिश की संभावना। "
    
    return summary.strip()