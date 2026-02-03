"""
State-Wise Extreme Weather Risk Calendar
Month-based risk assessment for different regions of India
No external APIs - pure rule-based logic
"""

from datetime import datetime


# ========================================
# STATE RISK MATRIX (Month-wise)
# ========================================

STATE_RISK_CALENDAR = {
    # Coastal States - Cyclone Prone
    'Odisha': {
        'Apr': ['cyclone_risk'],
        'May': ['cyclone_risk', 'heatwave_risk'],
        'Jun': ['cyclone_risk'],
        'Oct': ['cyclone_risk'],
        'Nov': ['cyclone_risk'],
        'Dec': ['cyclone_risk']
    },
    'West Bengal': {
        'Apr': ['cyclone_risk'],
        'May': ['cyclone_risk', 'heatwave_risk'],
        'Jun': ['cyclone_risk'],
        'Oct': ['cyclone_risk'],
        'Nov': ['cyclone_risk']
    },
    'Andhra Pradesh': {
        'Apr': ['cyclone_risk'],
        'May': ['cyclone_risk', 'heatwave_risk'],
        'Oct': ['cyclone_risk'],
        'Nov': ['cyclone_risk'],
        'Dec': ['cyclone_risk']
    },
    'Tamil Nadu': {
        'Oct': ['cyclone_risk'],
        'Nov': ['cyclone_risk'],
        'Dec': ['cyclone_risk'],
        'Apr': ['heatwave_risk'],
        'May': ['heatwave_risk']
    },
    'Kerala': {
        'May': ['cyclone_risk'],
        'Jun': ['heavy_rainfall'],
        'Jul': ['heavy_rainfall', 'flood_risk'],
        'Aug': ['heavy_rainfall', 'flood_risk'],
        'Sep': ['heavy_rainfall']
    },
    'Gujarat': {
        'May': ['cyclone_risk', 'heatwave_risk'],
        'Jun': ['cyclone_risk', 'heatwave_risk'],
        'Oct': ['cyclone_risk'],
        'Nov': ['cyclone_risk']
    },
    'Maharashtra': {
        'Jun': ['heavy_rainfall'],
        'Jul': ['heavy_rainfall'],
        'Aug': ['heavy_rainfall'],
        'Apr': ['heatwave_risk'],
        'May': ['heatwave_risk']
    },
    
    # Northern Plains - Heatwave & Cold Wave
    'Rajasthan': {
        'Apr': ['heatwave_risk'],
        'May': ['heatwave_risk'],
        'Jun': ['heatwave_risk'],
        'Dec': ['cold_wave'],
        'Jan': ['cold_wave', 'frost_risk']
    },
    'Punjab': {
        'May': ['heatwave_risk'],
        'Jun': ['heatwave_risk'],
        'Dec': ['cold_wave', 'fog_risk'],
        'Jan': ['cold_wave', 'frost_risk', 'fog_risk']
    },
    'Haryana': {
        'May': ['heatwave_risk'],
        'Jun': ['heatwave_risk'],
        'Dec': ['cold_wave', 'fog_risk'],
        'Jan': ['cold_wave', 'frost_risk', 'fog_risk']
    },
    'Uttar Pradesh': {
        'May': ['heatwave_risk'],
        'Jun': ['heatwave_risk'],
        'Dec': ['cold_wave', 'fog_risk'],
        'Jan': ['cold_wave', 'frost_risk', 'fog_risk']
    },
    'Delhi': {
        'May': ['heatwave_risk'],
        'Jun': ['heatwave_risk'],
        'Dec': ['cold_wave', 'fog_risk'],
        'Jan': ['cold_wave', 'frost_risk', 'fog_risk']
    },
    
    # Northeast - Heavy Rainfall & Floods
    'Assam': {
        'Jun': ['heavy_rainfall', 'flood_risk'],
        'Jul': ['heavy_rainfall', 'flood_risk'],
        'Aug': ['heavy_rainfall', 'flood_risk'],
        'Sep': ['heavy_rainfall', 'flood_risk']
    },
    'Meghalaya': {
        'Jun': ['heavy_rainfall'],
        'Jul': ['heavy_rainfall'],
        'Aug': ['heavy_rainfall']
    },
    
    # Central India
    'Madhya Pradesh': {
        'Apr': ['heatwave_risk'],
        'May': ['heatwave_risk'],
        'Jun': ['heatwave_risk'],
        'Dec': ['cold_wave']
    },
    'Chhattisgarh': {
        'Apr': ['heatwave_risk'],
        'May': ['heatwave_risk'],
        'Jun': ['heavy_rainfall']
    },
    
    # Eastern States
    'Bihar': {
        'May': ['heatwave_risk'],
        'Jun': ['heatwave_risk', 'flood_risk'],
        'Jul': ['flood_risk'],
        'Aug': ['flood_risk'],
        'Dec': ['cold_wave', 'fog_risk'],
        'Jan': ['cold_wave', 'fog_risk']
    },
    'Jharkhand': {
        'Apr': ['heatwave_risk'],
        'May': ['heatwave_risk'],
        'Jun': ['heatwave_risk']
    },
    
    # Southern States
    'Karnataka': {
        'Apr': ['heatwave_risk'],
        'May': ['heatwave_risk'],
        'Jun': ['heavy_rainfall']
    },
    'Telangana': {
        'Apr': ['heatwave_risk'],
        'May': ['heatwave_risk']
    },
    
    # Hill States
    'Himachal Pradesh': {
        'Dec': ['heavy_snowfall', 'frost_risk'],
        'Jan': ['heavy_snowfall', 'frost_risk'],
        'Feb': ['frost_risk']
    },
    'Uttarakhand': {
        'Dec': ['heavy_snowfall', 'frost_risk'],
        'Jan': ['heavy_snowfall', 'frost_risk']
    }
}


# ========================================
# RISK DEFINITIONS & ADVISORIES
# ========================================

RISK_ADVISORIES = {
    'cyclone_risk': {
        'name_en': 'Cyclone Risk',
        'name_hi': 'चक्रवात का खतरा',
        'icon': '🌀',
        'severity': 'danger',
        'message_en': 'Cyclone-prone season for this region',
        'message_hi': 'इस क्षेत्र के लिए चक्रवात-प्रवण मौसम',
        'action_en': 'Stay alert for weather updates. Secure loose objects. Prepare for strong winds and heavy rain.',
        'action_hi': 'मौसम अपडेट के लिए सतर्क रहें। ढीली वस्तुओं को सुरक्षित करें। तेज़ हवाओं और भारी बारिश के लिए तैयार रहें।',
        'farm_impact_en': 'Delay harvesting if crops are ready. Ensure proper drainage. Tie down greenhouse structures.',
        'farm_impact_hi': 'यदि फसल तैयार है तो कटाई में देरी करें। उचित जल निकासी सुनिश्चित करें।'
    },
    'heatwave_risk': {
        'name_en': 'Heatwave Alert',
        'name_hi': 'लू की चेतावनी',
        'icon': '🔥',
        'severity': 'warning',
        'message_en': 'High temperature risk for this month',
        'message_hi': 'इस महीने उच्च तापमान का खतरा',
        'action_en': 'Avoid outdoor work during 11 AM - 4 PM. Stay hydrated. Use protective gear.',
        'action_hi': '11 बजे से 4 बजे के बीच बाहर काम से बचें। हाइड्रेटेड रहें। सुरक्षात्मक उपकरण का उपयोग करें।',
        'farm_impact_en': 'Increase irrigation frequency. Water crops early morning or evening. Provide shade for sensitive crops.',
        'farm_impact_hi': 'सिंचाई की आवृत्ति बढ़ाएं। सुबह या शाम को फसलों को पानी दें। संवेदनशील फसलों के लिए छाया प्रदान करें।'
    },
    'cold_wave': {
        'name_en': 'Cold Wave Warning',
        'name_hi': 'शीत लहर चेतावनी',
        'icon': '❄️',
        'severity': 'warning',
        'message_en': 'Temperature may drop significantly',
        'message_hi': 'तापमान में काफी गिरावट हो सकती है',
        'action_en': 'Protect yourself from cold. Cover crops at night if possible.',
        'action_hi': 'ठंड से खुद को बचाएं। यदि संभव हो तो रात में फसलों को ढकें।',
        'farm_impact_en': 'Protect sensitive crops from frost. Delay early morning irrigation. Use smoke to prevent frost damage.',
        'farm_impact_hi': 'संवेदनशील फसलों को पाले से बचाएं। सुबह जल्दी सिंचाई में देरी करें। पाले की क्षति को रोकने के लिए धुएं का उपयोग करें।'
    },
    'frost_risk': {
        'name_en': 'Frost Risk',
        'name_hi': 'पाला का खतरा',
        'icon': '🧊',
        'severity': 'danger',
        'message_en': 'Frost conditions expected',
        'message_hi': 'पाला पड़ने की स्थिति संभावित',
        'action_en': 'Cover young plants. Light controlled fires for warmth in fields.',
        'action_hi': 'युवा पौधों को ढकें। खेतों में गर्माहट के लिए नियंत्रित आग जलाएं।',
        'farm_impact_en': 'Critical risk for young plants. Cover crops with plastic sheets. Irrigate lightly before sunset.',
        'farm_impact_hi': 'युवा पौधों के लिए गंभीर खतरा। फसलों को प्लास्टिक शीट से ढकें। सूर्यास्त से पहले हल्का सिंचाई करें।'
    },
    'heavy_rainfall': {
        'name_en': 'Heavy Rainfall Expected',
        'name_hi': 'भारी बारिश की संभावना',
        'icon': '🌧️',
        'severity': 'warning',
        'message_en': 'Monsoon season - expect intense rainfall',
        'message_hi': 'मानसून का मौसम - तेज बारिश की उम्मीद',
        'action_en': 'Check drainage systems. Avoid travel during heavy rain.',
        'action_hi': 'जल निकासी व्यवस्था की जांच करें। भारी बारिश के दौरान यात्रा से बचें।',
        'farm_impact_en': 'Ensure field drainage. Avoid pesticide spraying. Delay fertilizer application.',
        'farm_impact_hi': 'खेत की जल निकासी सुनिश्चित करें। कीटनाशक छिड़काव से बचें। उर्वरक के उपयोग में देरी करें।'
    },
    'flood_risk': {
        'name_en': 'Flood Risk',
        'name_hi': 'बाढ़ का खतरा',
        'icon': '🌊',
        'severity': 'danger',
        'message_en': 'High flood risk in low-lying areas',
        'message_hi': 'निचले इलाकों में बाढ़ का उच्च खतरा',
        'action_en': 'Move to higher ground if water levels rise. Monitor river/canal levels.',
        'action_hi': 'यदि जल स्तर बढ़े तो ऊंची जगह पर जाएं। नदी/नहर के स्तर की निगरानी करें।',
        'farm_impact_en': 'Harvest early if possible. Create drainage channels. Move equipment to safe areas.',
        'farm_impact_hi': 'यदि संभव हो तो जल्दी कटाई करें। जल निकासी चैनल बनाएं। उपकरण को सुरक्षित क्षेत्रों में स्थानांतरित करें।'
    },
    'fog_risk': {
        'name_en': 'Dense Fog Alert',
        'name_hi': 'घने कोहरे की चेतावनी',
        'icon': '🌫️',
        'severity': 'info',
        'message_en': 'Visibility may be severely reduced',
        'message_hi': 'दृश्यता गंभीर रूप से कम हो सकती है',
        'action_en': 'Drive carefully. Avoid early morning travel if possible.',
        'action_hi': 'सावधानी से ड्राइव करें। यदि संभव हो तो सुबह की यात्रा से बचें।',
        'farm_impact_en': 'Delay spraying operations. Wait for fog to clear before field work.',
        'farm_impact_hi': 'छिड़काव कार्य में देरी करें। खेत के काम से पहले कोहरे के साफ होने की प्रतीक्षा करें।'
    },
    'heavy_snowfall': {
        'name_en': 'Snowfall Expected',
        'name_hi': 'हिमपात की संभावना',
        'icon': '🌨️',
        'severity': 'warning',
        'message_en': 'Heavy snowfall expected in hilly areas',
        'message_hi': 'पहाड़ी इलाकों में भारी हिमपात की संभावना',
        'action_en': 'Stock essential supplies. Ensure livestock shelter is secure.',
        'action_hi': 'आवश्यक आपूर्ति स्टॉक करें। सुनिश्चित करें कि पशुधन आश्रय सुरक्षित है।',
        'farm_impact_en': 'Protect crops from snow load. Clear snow from greenhouse roofs. Ensure animal warmth.',
        'farm_impact_hi': 'बर्फ के भार से फसलों की रक्षा करें। ग्रीनहाउस की छतों से बर्फ साफ करें।'
    }
}


# ========================================
# HELPER FUNCTIONS
# ========================================

def get_current_month_risks(state_name):
    """
    Get weather risks for current month in given state
    Returns list of risk types
    """
    if not state_name:
        return []
    
    current_month = datetime.now().strftime('%b')  # 'Jan', 'Feb', etc.
    
    state_risks = STATE_RISK_CALENDAR.get(state_name, {})
    month_risks = state_risks.get(current_month, [])
    
    return month_risks


def get_state_risk_advisories(state_name):
    """
    Get detailed advisories for all risks in current month
    Returns bilingual advisory objects
    """
    risk_types = get_current_month_risks(state_name)
    
    if not risk_types:
        return []
    
    advisories = []
    for risk_type in risk_types:
        risk_info = RISK_ADVISORIES.get(risk_type, {})
        if risk_info:
            advisories.append({
                'advisory_key': risk_type.upper(),
                'name_en': risk_info['name_en'],
                'name_hi': risk_info['name_hi'],
                'icon': risk_info['icon'],
                'alert_type': risk_info['severity'],
                'message_en': risk_info['message_en'],
                'message_hi': risk_info['message_hi'],
                'suggested_action_en': risk_info['action_en'],
                'suggested_action_hi': risk_info['action_hi'],
                'farm_impact_en': risk_info['farm_impact_en'],
                'farm_impact_hi': risk_info['farm_impact_hi']
            })
    
    return advisories


def get_risk_summary_en(state_name):
    """Generate English risk summary for state"""
    advisories = get_state_risk_advisories(state_name)
    
    if not advisories:
        return f"No significant weather risks for {state_name} this month."
    
    risk_names = [adv['name_en'] for adv in advisories]
    return f"{state_name} - Active risks: {', '.join(risk_names)}"


def get_risk_summary_hi(state_name):
    """Generate Hindi risk summary for state"""
    advisories = get_state_risk_advisories(state_name)
    
    if not advisories:
        return f"{state_name} के लिए इस महीने कोई महत्वपूर्ण मौसम जोखिम नहीं।"
    
    risk_names = [adv['name_hi'] for adv in advisories]
    return f"{state_name} - सक्रिय जोखिम: {', '.join(risk_names)}"