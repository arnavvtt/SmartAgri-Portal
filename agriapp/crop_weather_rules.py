"""
Crop-Weather Knowledge Base for Indian Agriculture
No ML, no external libraries - just agricultural domain knowledge
This dictionary contains crop-specific parameters for weather-based advisory
"""

CROP_KNOWLEDGE_BASE = {
    # ============================================
    # RABI CROPS (Winter season: Oct-Mar)
    # ============================================
    "Wheat": {
        "season": "Rabi",
        "ideal_temp_min": 10,
        "ideal_temp_max": 25,
        "heat_stress_threshold": 30,
        "water_requirement": "MEDIUM",
        "crop_name_hi": "गेहूं"
    },
    "Mustard": {
        "season": "Rabi",
        "ideal_temp_min": 10,
        "ideal_temp_max": 27,
        "heat_stress_threshold": 32,
        "water_requirement": "LOW",
        "crop_name_hi": "सरसों"
    },
    "Chickpea": {
        "season": "Rabi",
        "ideal_temp_min": 15,
        "ideal_temp_max": 30,
        "heat_stress_threshold": 35,
        "water_requirement": "LOW",
        "crop_name_hi": "चना"
    },
    "Chana": {
        "season": "Rabi",
        "ideal_temp_min": 15,
        "ideal_temp_max": 30,
        "heat_stress_threshold": 35,
        "water_requirement": "LOW",
        "crop_name_hi": "चना"
    },
    "Barley": {
        "season": "Rabi",
        "ideal_temp_min": 12,
        "ideal_temp_max": 25,
        "heat_stress_threshold": 30,
        "water_requirement": "LOW",
        "crop_name_hi": "जौ"
    },
    
    # ============================================
    # KHARIF CROPS (Monsoon season: Jun-Oct)
    # ============================================
    "Rice": {
        "season": "Kharif",
        "ideal_temp_min": 20,
        "ideal_temp_max": 35,
        "heat_stress_threshold": 40,
        "water_requirement": "HIGH",
        "crop_name_hi": "धान"
    },
    "Paddy": {
        "season": "Kharif",
        "ideal_temp_min": 20,
        "ideal_temp_max": 35,
        "heat_stress_threshold": 40,
        "water_requirement": "HIGH",
        "crop_name_hi": "धान"
    },
    "Cotton": {
        "season": "Kharif",
        "ideal_temp_min": 21,
        "ideal_temp_max": 35,
        "heat_stress_threshold": 38,
        "water_requirement": "MEDIUM",
        "crop_name_hi": "कपास"
    },
    "Maize": {
        "season": "Kharif",
        "ideal_temp_min": 18,
        "ideal_temp_max": 32,
        "heat_stress_threshold": 37,
        "water_requirement": "MEDIUM",
        "crop_name_hi": "मक्का"
    },
    "Soybean": {
        "season": "Kharif",
        "ideal_temp_min": 20,
        "ideal_temp_max": 32,
        "heat_stress_threshold": 37,
        "water_requirement": "MEDIUM",
        "crop_name_hi": "सोयाबीन"
    },
    
    # ============================================
    # ZAID CROPS (Summer season: Mar-Jun)
    # ============================================
    "Watermelon": {
        "season": "Zaid",
        "ideal_temp_min": 24,
        "ideal_temp_max": 35,
        "heat_stress_threshold": 40,
        "water_requirement": "HIGH",
        "crop_name_hi": "तरबूज"
    },
    "Cucumber": {
        "season": "Zaid",
        "ideal_temp_min": 18,
        "ideal_temp_max": 30,
        "heat_stress_threshold": 35,
        "water_requirement": "MEDIUM",
        "crop_name_hi": "खीरा"
    },
    "Bitter Gourd": {
        "season": "Zaid",
        "ideal_temp_min": 24,
        "ideal_temp_max": 35,
        "heat_stress_threshold": 38,
        "water_requirement": "MEDIUM",
        "crop_name_hi": "करेला"
    },
    "Karela": {
        "season": "Zaid",
        "ideal_temp_min": 24,
        "ideal_temp_max": 35,
        "heat_stress_threshold": 38,
        "water_requirement": "MEDIUM",
        "crop_name_hi": "करेला"
    }
}


SEASON_FALLBACK_RULES = {
    "Rabi": {
        "ideal_temp_min": 10,
        "ideal_temp_max": 25,
        "heat_stress_threshold": 30,
        "water_requirement": "MEDIUM",
        "season_name_hi": "रबी"
    },
    "Kharif": {
        "ideal_temp_min": 20,
        "ideal_temp_max": 35,
        "heat_stress_threshold": 38,
        "water_requirement": "HIGH",
        "season_name_hi": "खरीफ"
    },
    "Zaid": {
        "ideal_temp_min": 22,
        "ideal_temp_max": 33,
        "heat_stress_threshold": 38,
        "water_requirement": "MEDIUM",
        "season_name_hi": "जायद"
    }
}


def get_crop_rules(crop_name):
    normalized_name = crop_name.strip().title()
    return CROP_KNOWLEDGE_BASE.get(normalized_name, None)


def get_season_rules(season_name):
    normalized_season = season_name.strip().title()
    return SEASON_FALLBACK_RULES.get(normalized_season, None)