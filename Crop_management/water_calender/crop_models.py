import numpy as np
import json
from datetime import datetime, timedelta
from Crop_management.water_calender.config import (
    MASTER_CROP_DATABASE, SOIL_WATER_PROPERTIES, 
    ASSUMED_ROOT_DEPTH_METERS, MANAGEMENT_ALLOWED_DEPLETION,
    FERTILIZER_COMPOSITION, OPENWEATHER_API_KEY, NPK_MODEL_API_URL, MM_TO_LITERS_PER_ACRE
)

DEFAULT_IRRIGATION_EFFICIENCY = 0.75

class CropCalendar:
    def __init__(self, crop_name, soil_type, area_acres):
        if crop_name not in MASTER_CROP_DATABASE: raise ValueError(f"Crop '{crop_name}' data is missing.")
        if soil_type not in SOIL_WATER_PROPERTIES: raise ValueError(f"Soil type '{soil_type}' data is missing.")
            
        self.crop_name = crop_name
        self.soil_type = soil_type
        self.area_acres = area_acres 
        self.crop_data = MASTER_CROP_DATABASE[self.crop_name]
        self.soil_props = SOIL_WATER_PROPERTIES[self.soil_type]
        self.total_days = self.crop_data['total_days']
        self.irrigation_efficiency = DEFAULT_IRRIGATION_EFFICIENCY
        self.current_soil_depletion_mm = 0.0

    def _calculate_taw_mm(self, root_depth_m):
        """Calculates Total Available Water (TAW) in mm for the current root depth."""
        taw_per_meter = self.soil_props['available_water_decimal'] * 1000 
        return taw_per_meter * root_depth_m

    def _get_weather_data(self, lat, lon, current_temp_c=None, current_humidity_perc=None):
        """
        [WEATHER API FETCH POINT] Fetches weather data (T, RH, WS, Rain). JSON T/RH overrides defaults.
        """
        default_weather = {
            'T2M': 25.0, 'RH2M': 60.0, 'WS2M': 2.0, 
            'ALLSKY_SFC_SW_DWN': 20.0, 'PRECTOTCORR': 1.0  
        }
        
        if current_temp_c is not None:
            default_weather['T2M'] = current_temp_c
        if current_humidity_perc is not None:
            default_weather['RH2M'] = current_humidity_perc
            
        return default_weather


    def _get_npk_model_advice(self, days_sown, crop_name):
        """
        [NPK MODEL API FETCH POINT] Fetches the required NPK dose from the external model API.
        """
        try:
         
            npk_schedule = self.crop_data.get('npk_schedule_per_acre', {})
            dose = npk_schedule.get(days_sown)
            
            if dose:
                k_req = dose['k']; p_req = dose['p']; n_req = dose['n']; comp = FERTILIZER_COMPOSITION
                mop_kg_acre = k_req / comp['mop']['k'] if comp['mop']['k'] > 0 else 0
                dap_kg_acre = p_req / comp['dap']['p'] if comp['dap']['p'] > 0 else 0
                n_from_dap = dap_kg_acre * comp['dap']['n']
                urea_kg_acre = max(0, n_req - n_from_dap) / comp['urea']['n']
                
                return {
                    'urea_kg': round(urea_kg_acre * self.area_acres, 2),
                    'dap_kg': round(dap_kg_acre * self.area_acres, 2),
                    'mop_kg': round(mop_kg_acre * self.area_acres, 2),
                    'note': dose.get('note', 'Model Recommended Dose')
                }
            return "No fertilizer scheduled for this day"
        except Exception:
            return "Error fetching NPK dose from model API"
    
    def _calculate_et0(self, weather_data):
       
        T = weather_data['T2M']; RH = weather_data['RH2M']; U2 = weather_data['WS2M']
        Rn_MJ = weather_data['ALLSKY_SFC_SW_DWN'] * 0.408; G = 0
        P = 101.3 * ((293 - 0.0065 * 100) / 293)**5.26
        delta = (4098 * (0.6108 * np.exp(17.27 * T / (T + 237.3)))) / ((T + 237.3) ** 2)
        gamma = 0.000665 * P; es = 0.6108 * np.exp(17.27 * T / (T + 237.3)); ea = (RH / 100) * es
        numerator = 0.408 * delta * (Rn_MJ - G) + gamma * (900 / (T + 273)) * U2 * (es - ea)
        denominator = delta + gamma * (1 + 0.34 * U2)
        if denominator == 0: return 0
        return max(numerator / denominator, 0)

    def _get_daily_params(self, days_sown):
        
        days = self.total_days; initial_duration = int(days * 0.20); late_duration = int(days * 0.20)
        stage_key = "initial" if days_sown <= initial_duration else "mid" if days_sown <= days - late_duration else "late"
        kc = self.crop_data['kc'].get(stage_key, 1.0)
        stage = stage_key.capitalize()
        root_depth_m = ASSUMED_ROOT_DEPTH_METERS.get(stage_key, ASSUMED_ROOT_DEPTH_METERS['late'])
        return stage_key, kc, stage, root_depth_m


    def get_daily_advice(self, days_sown, lat, lon, current_temp_c=None, current_humidity_perc=None):
        """Calculates the irrigation and fertilizer needs for a specific day."""
      
        weather_data = self._get_weather_data(lat, lon, current_temp_c, current_humidity_perc)
        et0 = self._calculate_et0(weather_data)
        rainfall_mm = weather_data['PRECTOTCORR']
        
        stage_key, kc, stage, root_depth_m = self._get_daily_params(days_sown)
        etc_mm = et0 * kc
     
        taw_mm = self._calculate_taw_mm(root_depth_m)
        raw_mm = taw_mm * MANAGEMENT_ALLOWED_DEPLETION
      
        net_loss_gain = etc_mm - rainfall_mm
        self.current_soil_depletion_mm += net_loss_gain
        self.current_soil_depletion_mm = max(0, self.current_soil_depletion_mm)

        irrigation_needed_mm = 0
     
        if rainfall_mm > etc_mm: 
            irrigation_needed_mm = 0
       
        elif self.crop_name == 'Paddy (Rice)' and self.current_soil_depletion_mm > 5.0: 
            irrigation_needed_mm = self.current_soil_depletion_mm + 50 
      
        elif self.current_soil_depletion_mm > raw_mm:
            irrigation_needed_mm = self.current_soil_depletion_mm
      
        gross_irrigation_mm = 0
        if irrigation_needed_mm > 0:
            gross_irrigation_mm = irrigation_needed_mm / self.irrigation_efficiency
            self.current_soil_depletion_mm -= irrigation_needed_mm 
            self.current_soil_depletion_mm = max(0, self.current_soil_depletion_mm)

        fertilizer_advice = self._get_npk_model_advice(days_sown, self.crop_name)

        return {
            'day': days_sown, 'stage': stage, 'rainfall_mm': round(rainfall_mm, 2),
            'current_depletion_mm': round(self.current_soil_depletion_mm, 2), 
            'trigger_point_mm': round(raw_mm, 2),
            'irrigation_to_apply_mm': round(gross_irrigation_mm, 2),
            'fertilizer_advice': fertilizer_advice,
            'taw_mm': round(taw_mm, 2)
        }
