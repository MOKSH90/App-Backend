# FERTILIZER_COMPOSITION = {
#     'urea': {'n': 0.46, 'p': 0, 'k': 0},
#     'dap': {'n': 0.18, 'p': 0.46, 'k': 0},
#     'mop': {'n': 0, 'p': 0, 'k': 0.60}
# }

# STATE_SOIL_NPK = { #dummy
#     'punjab': {'n': 25, 'p': 15, 'k': 20},
#     'haryana': {'n': 24, 'p': 14, 'k': 19},
#     'up': {'n': 23, 'p': 13, 'k': 18},
#     'bihar': {'n': 20, 'p': 10, 'k': 15},
#     'wb': {'n': 21, 'p': 11, 'k': 16},
#     'mp': {'n': 22, 'p': 12, 'k': 17},
#     'maharashtra': {'n': 18, 'p': 8, 'k': 12},
#     'gujarat': {'n': 19, 'p': 9, 'k': 13},
#     'rajasthan': {'n': 17, 'p': 7, 'k': 11},
#     'tamilnadu': {'n': 22, 'p': 12, 'k': 18},
#     'karnataka': {'n': 21, 'p': 11, 'k': 17},
#     'kerala': {'n': 23, 'p': 13, 'k': 19},
#      'andhra': {'n': 20, 'p': 10, 'k': 16},
#     'telangana': {'n': 19, 'p': 9, 'k': 15},
#     'assam': {'n': 22, 'p': 12, 'k': 18},
#     'odisha': {'n': 21, 'p': 11, 'k': 17}
# }

SOIL_WATER_PROPERTIES = {
    "alluvial": {"available_water_decimal": 0.19},
    "clayey": {"available_water_decimal": 0.18},
    "loamy": {"available_water_decimal": 0.16},
    "sandy": {"available_water_decimal": 0.07},
    "black": {"available_water_decimal": 0.20},
    "red and yellow": {"available_water_decimal": 0.13},
    "laterite": {"available_water_decimal": 0.09},
    "arid": {"available_water_decimal": 0.09},
    "forest": {"available_water_decimal": 0.17},
}

ASSUMED_ROOT_DEPTH_METERS = {
    "initial": 0.2,
    "mid": 0.6,
    "late": 0.5
}


MANAGEMENT_ALLOWED_DEPLETION = 0.5 
HECTARE_TO_ACRE = 0.404686 

MASTER_CROP_DATABASE = {
   
    "Wheat": {
        "watering_interval_days": 15,
        "kc": {"initial": 0.35, "mid": 1.15, "late": 0.40},
        "sunlight_hours": "6+ hours",
        "total_days": 130,
        "npk_schedule_per_acre": { 
            1: {"n": 25, "p": 15, "k": 10, "note": "Basal Dose: Urea + DAP + MOP"},
            20: {"n": 20, "p": 0, "k": 0, "note": "Mid: Crown Root Initiation / Tillering (Only Nitrogen)"},
            45: {"n": 15, "p": 0, "k": 0, "note": "Last: Before Heading / Booting (Boost tillers)"}
        },
        "npk_total": {"n": 60, "p": 15, "k": 10}
    },
    "Paddy (Rice)": {
        "watering_interval_days": 2, 
        "kc": {"initial": 1.05, "mid": 1.20, "late": 0.95},
        "sunlight_hours": "6-8 hours",
        "total_days": 140,
        "npk_schedule_per_acre": {
            1: {"n": 20, "p": 10, "k": 15, "note": "Basal Dose: Transplanting (DAP + MOP)"},
            30: {"n": 18, "p": 0, "k": 5, "note": "Mid: Tillering (Nitrogen booster)"},
            45: {"n": 12, "p": 0, "k": 5, "note": "Last: Panicle Initiation (Grain formation support)"}
        },
        "npk_total": {"n": 50, "p": 10, "k": 25} 
    },
    "Maize": {
        "watering_interval_days": 6, 
        "kc": {"initial": 0.35, "mid": 1.20, "late": 0.60},
        "sunlight_hours": "6-8 hours",
        "total_days": 105,
        "npk_schedule_per_acre": {
            1: {"n": 20, "p": 10, "k": 10, "note": "Basal Dose: Sowing (Starter fertilizer)"},
            25: {"n": 30, "p": 0, "k": 5, "note": "Mid: Knee-high / Vegetative (Rapid growth)"},
            45: {"n": 20, "p": 0, "k": 5, "note": "Last: Before Tasseling (Cob filling support)"}
        },
        "npk_total": {"n": 70, "p": 10, "k": 20} 
    },
  
    
    "Banana": {
        "watering_interval_days": 2, "kc": {"initial": 0.50, "mid": 1.10, "late": 0.90}, "sunlight_hours": "6-8 hours", "total_days": 400,
        "npk_total": {"n": 121.4, "p": 60.7, "k": 182.1}, 
        "npk_schedule_per_acre": {
            1: {"n": 48.6, "p": 60.7, "k": 182.1, "note": "Basal Dose (Generic)"},
            161: {"n": 36.4, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
            241: {"n": 36.4, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Brinjal": {
        "watering_interval_days": 2, "kc": {"initial": 0.60, "mid": 1.10, "late": 0.90}, "sunlight_hours": "6+ hours", "total_days": 135,
        "npk_total": {"n": 48.6, "p": 24.3, "k": 28.3}, 
        "npk_schedule_per_acre": {
            1: {"n": 19.4, "p": 24.3, "k": 28.3, "note": "Basal Dose (Generic)"},
            54: {"n": 14.6, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	81: {"n": 14.6, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Cabbage": {
        "watering_interval_days": 2, "kc": {"initial": 0.70, "mid": 1.05, "late": 0.95}, "sunlight_hours": "6-8 hours", "total_days": 105,
        "npk_total": {"n": 40.5, "p": 20.2, "k": 20.2}, 
        "npk_schedule_per_acre": {
            1: {"n": 16.2, "p": 20.2, "k": 20.2, "note": "Basal Dose (Generic)"},
            42: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	63: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Cauliflower": {
        "watering_interval_days": 2, "kc": {"initial": 0.70, "mid": 1.05, "late": 0.95}, "sunlight_hours": "6+ hours", "total_days": 105,
        "npk_total": {"n": 40.5, "p": 20.2, "k": 20.2}, 
        "npk_schedule_per_acre": {
            1: {"n": 16.2, "p": 20.2, "k": 20.2, "note": "Basal Dose (Generic)"},
            42: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	63: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Cucumber": {
        "watering_interval_days": 1, "kc": {"initial": 0.60, "mid": 1.00, "late": 0.75}, "sunlight_hours": "6-8 hours", "total_days": 70,
        "npk_total": {"n": 40.5, "p": 20.2, "k": 32.4}, 
        "npk_schedule_per_acre": {
            1: {"n": 16.2, "p": 20.2, "k": 32.4, "note": "Basal Dose (Generic)"},
            28: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	42: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Garlic": {
        "watering_interval_days": 3, "kc": {"initial": 0.70, "mid": 1.05, "late": 0.80}, "sunlight_hours": "6-8 hours", "total_days": 195,
        "npk_total": {"n": 40.5, "p": 20.2, "k": 20.2}, 
        "npk_schedule_per_acre": {
            1: {"n": 16.2, "p": 20.2, "k": 20.2, "note": "Basal Dose (Generic)"},
            78: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	117: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Ginger": {
        "watering_interval_days": 3, "kc": {"initial": 0.75, "mid": 1.1, "late": 0.8}, "sunlight_hours": "3-5 hours", "total_days": 220,
        "npk_total": {"n": 60.7, "p": 30.4, "k": 40.5}, 
        "npk_schedule_per_acre": {
            1: {"n": 24.3, "p": 30.4, "k": 40.5, "note": "Basal Dose (Generic)"},
            88: {"n": 18.2, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	132: {"n": 18.2, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Green Chilli": {
        "watering_interval_days": 2, "kc": {"initial": 0.60, "mid": 1.05, "late": 0.90}, "sunlight_hours": "6+ hours", "total_days": 135,
        "npk_total": {"n": 48.6, "p": 24.3, "k": 28.3}, 
        "npk_schedule_per_acre": {
            1: {"n": 19.4, "p": 24.3, "k": 28.3, "note": "Basal Dose (Generic)"},
            54: {"n": 14.6, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	81: {"n": 14.6, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Okra": {
        "watering_interval_days": 2, "kc": {"initial": 0.60, "mid": 1.10, "late": 0.90}, "sunlight_hours": "6-8 hours", "total_days": 55,
        "npk_total": {"n": 40.5, "p": 20.2, "k": 20.2},
        "npk_schedule_per_acre": {
            1: {"n": 16.2, "p": 20.2, "k": 20.2, "note": "Basal Dose (Generic)"},
            22: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	33: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Onion": {
        "watering_interval_days": 3, "kc": {"initial": 0.70, "mid": 1.05, "late": 0.80}, "sunlight_hours": "6+ hours", "total_days": 135,
        "npk_total": {"n": 40.5, "p": 20.2, "k": 40.5},
        "npk_schedule_per_acre": {
            1: {"n": 16.2, "p": 20.2, "k": 40.5, "note": "Basal Dose (Generic)"},
            54: {"n": 14.6, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	81: {"n": 14.6, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Peas": {
        "watering_interval_days": 6, "kc": {"initial": 0.50, "mid": 1.15, "late": 1.05}, "sunlight_hours": "6+ hours", "total_days": 80,
        "npk_total": {"n": 8.1, "p": 24.3, "k": 12.1}, 
        "npk_schedule_per_acre": {
            1: {"n": 3.2, "p": 24.3, "k": 12.1, "note": "Basal Dose (Generic)"},
            32: {"n": 2.4, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	48: {"n": 2.4, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Potato": {
        "watering_interval_days": 4, "kc": {"initial": 0.50, "mid": 1.15, "late": 0.75}, "sunlight_hours": "6+ hours", "total_days": 100,
        "npk_total": {"n": 44.5, "p": 22.3, "k": 34.4}, 
        "npk_schedule_per_acre": {
            1: {"n": 17.8, "p": 22.3, "k": 34.4, "note": "Basal Dose (Generic)"},
            40: {"n": 13.4, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	60: {"n": 13.4, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Tomato": {
        "watering_interval_days": 2, "kc": {"initial": 0.60, "mid": 1.15, "late": 0.85}, "sunlight_hours": "6-8 hours", "total_days": 120,
        "npk_total": {"n": 60.7, "p": 32.4, "k": 32.4}, 
        "npk_schedule_per_acre": {
            1: {"n": 24.3, "p": 32.4, "k": 32.4, "note": "Basal Dose (Generic)"},
            48: {"n": 18.2, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	72: {"n": 18.2, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Watermelon": {
        "watering_interval_days": 4, "kc": {"initial": 0.40, "mid": 1.00, "late": 0.75}, "sunlight_hours": "8+ hours", "total_days": 80,
        "npk_total": {"n": 32.4, "p": 24.3, "k": 48.6}, 
        "npk_schedule_per_acre": {
            1: {"n": 13.0, "p": 24.3, "k": 48.6, "note": "Basal Dose (Generic)"},
            32: {"n": 9.7, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	48: {"n": 9.7, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Bajra": {
        "watering_interval_days": 7, "kc": {"initial": 0.30, "mid": 1.05, "late": 0.55}, "sunlight_hours": "6-8 hours", "total_days": 80,
        "npk_total": {"n": 32.4, "p": 16.2, "k": 12.1}, 
        "npk_schedule_per_acre": {
            1: {"n": 13.0, "p": 16.2, "k": 12.1, "note": "Basal Dose (Generic)"},
            32: {"n": 9.7, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	48: {"n": 9.7, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Cotton": {
        "watering_interval_days": 7, "kc": {"initial": 0.35, "mid": 1.20, "late": 0.60}, "sunlight_hours": "8-10 hours", "total_days": 165,
        "npk_total": {"n": 40.5, "p": 20.2, "k": 28.3}, 
        "npk_schedule_per_acre": {
            1: {"n": 16.2, "p": 20.2, "k": 28.3, "note": "Basal Dose (Generic)"},
            66: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	99: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Guava": {
        "watering_interval_days": 7, "kc": {"initial": 0.50, "mid": 0.80, "late": 0.65}, "sunlight_hours": "6-8 hours", "total_days": 365,
        "npk_total": {"n": 60.7, "p": 20.2, "k": 40.5},
        "npk_schedule_per_acre": {
            1: {"n": 24.3, "p": 20.2, "k": 40.5, "note": "Basal Dose (Generic)"},
            146: {"n": 18.2, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	219: {"n": 18.2, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Jowar": {
        "watering_interval_days": 7, "kc": {"initial": 0.30, "mid": 1.05, "late": 0.55}, "sunlight_hours": "6+ hours", "total_days": 110,
        "npk_total": {"n": 40.5, "p": 20.2, "k": 16.2}, 
        "npk_schedule_per_acre": {
            1: {"n": 16.2, "p": 20.2, "k": 16.2, "note": "Basal Dose (Generic)"},
            44: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	66: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Lemon": {
        "watering_interval_days": 7, "kc": {"initial": 0.60, "mid": 0.75, "late": 0.65}, "sunlight_hours": "6-8 hours", "total_days": 365,
        "npk_total": {"n": 40.5, "p": 16.2, "k": 32.4}, 
        "npk_schedule_per_acre": {
            1: {"n": 16.2, "p": 16.2, "k": 32.4, "note": "Basal Dose (Generic)"},
            146: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	219: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Mango": {
        "watering_interval_days": 7, "kc": {"initial": 0.55, "mid": 0.85, "late": 0.70}, "sunlight_hours": "6+ hours", "total_days": 365,
        "npk_total": {"n": 40.5, "p": 16.2, "k": 32.4},
        "npk_schedule_per_acre": {
            1: {"n": 16.2, "p": 16.2, "k": 32.4, "note": "Basal Dose (Generic)"},
            146: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	219: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Mustard": {
        "watering_interval_days": 15, "kc": {"initial": 0.35, "mid": 1.10, "late": 0.35}, "sunlight_hours": "6+ hours", "total_days": 120,
        "npk_total": {"n": 32.4, "p": 16.2, "k": 16.2}, 
        "npk_schedule_per_acre": {
            1: {"n": 13.0, "p": 16.2, "k": 16.2, "note": "Basal Dose (Generic)"},
            48: {"n": 9.7, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	72: {"n": 9.7, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Orange": {
        "watering_interval_days": 10, "kc": {"initial": 0.60, "mid": 0.75, "late": 0.65}, "sunlight_hours": "6-8 hours", "total_days": 365,
        "npk_total": {"n": 40.5, "p": 16.2, "k": 32.4}, 
        "npk_schedule_per_acre": {
            1: {"n": 16.2, "p": 16.2, "k": 32.4, "note": "Basal Dose (Generic)"},
            146: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	219: {"n": 12.1, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Soyabean": {
        "watering_interval_days": 10, "kc": {"initial": 0.40, "mid": 1.15, "late": 0.50}, "sunlight_hours": "6+ hours", "total_days": 100,
        "npk_total": {"n": 8.1, "p": 24.3, "k": 16.2}, 
        "npk_schedule_per_acre": {
            1: {"n": 3.2, "p": 24.3, "k": 16.2, "note": "Basal Dose (Generic)"},
            40: {"n": 2.4, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	60: {"n": 2.4, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Sugarcane": {
        "watering_interval_days": 7, "kc": {"initial": 0.40, "mid": 1.25, "late": 0.75}, "sunlight_hours": "8-10 hours", "total_days": 365,
        "npk_total": {"n": 101.2, "p": 32.4, "k": 48.6}, 
        "npk_schedule_per_acre": {
            1: {"n": 40.5, "p": 32.4, "k": 48.6, "note": "Basal Dose (Generic)"},
            146: {"n": 30.4, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	219: {"n": 30.4, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
    "Sunflower": {
        "watering_interval_days": 10, "kc": {"initial": 0.35, "mid": 1.15, "late": 0.45}, "sunlight_hours": "6-8 hours", "total_days": 90,
        "npk_total": {"n": 32.4, "p": 16.2, "k": 16.2}, 
        "npk_schedule_per_acre": {
            1: {"n": 13.0, "p": 16.2, "k": 16.2, "note": "Basal Dose (Generic)"},
            36: {"n": 9.7, "p": 0, "k": 0, "note": "Top Dressing 1 (Generic)"},
        	54: {"n": 9.7, "p": 0, "k": 0, "note": "Top Dressing 2 (Generic)"}
        }
    },
}