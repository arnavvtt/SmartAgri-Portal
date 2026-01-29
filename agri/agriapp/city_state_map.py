"""
City to State Mapping
Used for location-based weather risk analysis
Covers major Indian cities
"""

CITY_STATE_MAP = {
    # Metro Cities
    'Delhi': 'Delhi',
    'New Delhi': 'Delhi',
    'Mumbai': 'Maharashtra',
    'Kolkata': 'West Bengal',
    'Chennai': 'Tamil Nadu',
    'Bangalore': 'Karnataka',
    'Bengaluru': 'Karnataka',
    'Hyderabad': 'Telangana',
    'Ahmedabad': 'Gujarat',
    'Pune': 'Maharashtra',
    
    # Northern States
    'Jaipur': 'Rajasthan',
    'Lucknow': 'Uttar Pradesh',
    'Kanpur': 'Uttar Pradesh',
    'Chandigarh': 'Punjab',
    'Amritsar': 'Punjab',
    'Ludhiana': 'Punjab',
    'Shimla': 'Himachal Pradesh',
    'Dehradun': 'Uttarakhand',
    
    # Eastern States
    'Patna': 'Bihar',
    'Ranchi': 'Jharkhand',
    'Bhubaneswar': 'Odisha',
    'Cuttack': 'Odisha',
    'Guwahati': 'Assam',
    
    # Western States
    'Surat': 'Gujarat',
    'Vadodara': 'Gujarat',
    'Rajkot': 'Gujarat',
    'Nagpur': 'Maharashtra',
    'Nashik': 'Maharashtra',
    
    # Southern States
    'Coimbatore': 'Tamil Nadu',
    'Madurai': 'Tamil Nadu',
    'Kochi': 'Kerala',
    'Thiruvananthapuram': 'Kerala',
    'Vijayawada': 'Andhra Pradesh',
    'Visakhapatnam': 'Andhra Pradesh',
    'Mysore': 'Karnataka',
    'Mangalore': 'Karnataka',
    
    # Central States
    'Bhopal': 'Madhya Pradesh',
    'Indore': 'Madhya Pradesh',
    'Raipur': 'Chhattisgarh',
}


def get_state_from_city(city_name):
    """
    Get state name from city
    Returns None if city not found in mapping
    """
    city_normalized = city_name.strip().title()
    return CITY_STATE_MAP.get(city_normalized, None)