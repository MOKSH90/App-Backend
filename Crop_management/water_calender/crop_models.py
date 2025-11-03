import requests
import numpy as np
from config import (
    MASTER_CROP_DATABASE, SOIL_WATER_PROPERTIES,
    ASSUMED_ROOT_DEPTH_METERS, MANAGEMENT_ALLOWED_DEPLETION,
    FERTILIZER_COMPOSITION, STATE_SOIL_NPK, HECTARE_TO_ACRE
)

DEFAULT_IRRIGATION_EFFICIENCY = 0.75

class CropCalendar:
    def __init__(self, crop_name, soil_type, state, area_acres):
        if crop_name not in MASTER_CROP_DATABASE:
            raise ValueError(f"Crop '{crop_name}' data is missing.")
        if soil_type not in SOIL_WATER_PROPERTIES:
            raise ValueError(f"Soil type '{soil_type}' data is missing.")
        if state.lower() not in STATE_SOIL_NPK:
            raise ValueError(f"State '{state}' data is missing.")
        self.crop_name = crop_name
        self.soil_type = soil_type
        self.state = state.lower()
        self.area_acres = area_acres 
        self.crop_data = MASTER_CROP_DATABASE[self.crop_name]
        self.soil_props = SOIL_WATER_PROPERTIES[self.soil_type]
        self.irrigation_efficiency = DEFAULT_IRRIGATION_EFFICIENCY
        self.total_days = self.crop_data['total_days']
        self.current_soil_depletion_mm = 0.0
        self.stage_duration = self._calculate_stage_duration()
        self.fertilizer_plan = self._calculate_seasonal_fertilizer_plan()
        self.fertilizer_schedule = self._prepare_fertilizer_schedule()
        
    def _calculate_stage_duration(self):
        days = self.total_days
        initial_duration = int(days * 0.20)
        late_duration = int(days * 0.20)
        mid_duration = days - initial_duration - late_duration
        stages = {
            "initial": {"duration": initial_duration, "start": 1, "end": initial_duration},
            "mid": {"duration": mid_duration, "start": initial_duration + 1, "end": initial_duration + mid_duration},
            "late": {"duration": late_duration, "start": initial_duration + mid_duration + 1, "end": days}
        }
        stages['late']['duration'] = stages['late']['end'] - stages['late']['start'] + 1
        return stages
        
    class WeatherService:
        def __init__(self, latitude=28.97, longitude=77.02):
            self.latitude = latitude
            self.longitude = longitude

        def _get_weather_data(self):
            try:
                url = (
                    f"https://api.open-meteo.com/v1/forecast?"
                    f"latitude={self.latitude}&longitude={self.longitude}"
                    f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,"
                    f"surface_solar_radiation,precipitation"
                )
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json().get("current", {})
                return {
                    "T2M": data.get("temperature_2m", 25.0),
                    "RH2M": data.get("relative_humidity_2m", 60.0),
                    "WS2M": data.get("wind_speed_10m", 2.0),
                    "ALLSKY_SFC_SW_DWN": data.get("surface_solar_radiation", 20.0),
                    "PRECTOTCORR": data.get("precipitation", 0.0),
                }
            except Exception as e:
                print(f"Error fetching weather data: {e}")
                return {
                    "T2M": 25.0,
                    "RH2M": 60.0,
                    "WS2M": 2.0,
                    "ALLSKY_SFC_SW_DWN": 20.0,
                    "PRECTOTCORR": np.random.choice([0, 0, 0, 0, 0, 0, 5, 10]),
                }
        
    def _calculate_et0(self, weather_data):
        T = weather_data['T2M']
        RH = weather_data['RH2M']
        U2 = weather_data['WS2M']
        Rn_MJ = weather_data['ALLSKY_SFC_SW_DWN'] * 0.408
        G = 0
        P = 101.3 * ((293 - 0.0065 * 100) / 293)**5.26
        delta = (4098 * (0.6108 * np.exp(17.27 * T / (T + 237.3)))) / ((T + 237.3) ** 2)
        gamma = 0.000665 * P
        es = 0.6108 * np.exp(17.27 * T / (T + 237.3))
        ea = (RH / 100) * es
        numerator = 0.408 * delta * (Rn_MJ - G) + gamma * (900 / (T + 273)) * U2 * (es - ea)
        denominator = delta + gamma * (1 + 0.34 * U2)
        if denominator == 0:
            return 0
        et0 = numerator / denominator
        return max(et0, 0)
        
    def _get_daily_params(self, days_sown):
        kc_data = self.crop_data['kc']
        stages = self.stage_duration
        current_stage = "N/A"
        root_depth_key = "initial"
        for name, data in stages.items():
            if data['start'] <= days_sown <= data['end']:
                current_stage = name
                root_depth_key = name
                break
        kc = kc_data.get(current_stage, kc_data['initial'])
        root_depth_m = ASSUMED_ROOT_DEPTH_METERS.get(root_depth_key, ASSUMED_ROOT_DEPTH_METERS['late'])
        return kc, current_stage.capitalize(), root_depth_m
    
    def _calculate_seasonal_fertilizer_plan(self):
        if 'npk_schedule_per_acre' in self.crop_data:
            comp = FERTILIZER_COMPOSITION
            schedule_kg_per_acre = self.crop_data['npk_schedule_per_acre']
            final_schedule = {}
            for day, npk_dose in schedule_kg_per_acre.items():
                k_req = npk_dose['k']
                p_req = npk_dose['p']
                n_req = npk_dose['n']
                mop_kg_acre = k_req / comp['mop']['k'] if comp['mop']['k'] > 0 else 0
                dap_kg_acre = p_req / comp['dap']['p'] if comp['dap']['p'] > 0 else 0
                n_from_dap = dap_kg_acre * comp['dap']['n']
                n_remaining = n_req - n_from_dap
                urea_kg_acre = n_remaining / comp['urea']['n'] if comp['urea']['n'] > 0 else 0
                urea_kg_acre = max(urea_kg_acre, 0)
                final_schedule[day] = {
                    'urea_kg': round(urea_kg_acre * self.area_acres, 2),
                    'dap_kg': round(dap_kg_acre * self.area_acres, 2),
                    'mop_kg': round(mop_kg_acre * self.area_acres, 2),
                    'note': npk_dose.get('note', 'User defined NPK split')
                }
            return final_schedule
        if 'npk_total' not in self.crop_data:
            return {"Note": "NPK data missing for this crop."}
        soil_npk = STATE_SOIL_NPK[self.state] 
        req_npk = self.crop_data['npk_total']
        n_gap = max(req_npk['n'] - soil_npk['n'], 0)
        p_gap = max(req_npk['p'] - soil_npk['p'], 0)
        k_gap = max(req_npk['k'] - soil_npk['k'], 0)
        comp = FERTILIZER_COMPOSITION
        mop_kg_ha = k_gap / comp['mop']['k'] if comp['mop']['k'] > 0 else 0
        dap_kg_ha = p_gap / comp['dap']['p'] if comp['dap']['p'] > 0 else 0
        n_from_dap = dap_kg_ha * comp['dap']['n']
        n_gap_remaining = n_gap - n_from_dap
        urea_kg_ha = n_gap_remaining / comp['urea']['n'] if comp['urea']['n'] > 0 else 0
        urea_kg_ha = max(urea_kg_ha, 0)
        conversion_factor = HECTARE_TO_ACRE * self.area_acres
        splits = {
            'basal_sowing_dose': {
                'urea_kg': round(urea_kg_ha * 0.4 * conversion_factor, 2),
                'dap_kg': round(dap_kg_ha * conversion_factor, 2),
                'mop_kg': round(mop_kg_ha * conversion_factor, 2)
            },
            'top_dressing_1_mid_early': {
                'urea_kg': round(urea_kg_ha * 0.3 * conversion_factor, 2),
                'dap_kg': 0,
                'mop_kg': 0
            },
            'top_dressing_2_mid_late': {
                'urea_kg': round(urea_kg_ha * 0.3 * conversion_factor, 2),
                'dap_kg': 0,
                'mop_kg': 0
            }
        }
        return splits
     
    def _prepare_fertilizer_schedule(self):
        schedule = {}
        if 'npk_schedule_per_acre' in self.crop_data:
            for day_num, dose in self.fertilizer_plan.items():
                schedule[day_num] = dose
            return schedule
        if 'basal_sowing_dose' in self.fertilizer_plan:
            schedule[1] = self.fertilizer_plan['basal_sowing_dose']
            mid_start = self.stage_duration['mid']['start']
            mid_duration = self.stage_duration['mid']['duration']
            day_td1 = mid_start + int(mid_duration / 3)
            if 'top_dressing_1_mid_early' in self.fertilizer_plan:
                schedule[day_td1] = self.fertilizer_plan['top_dressing_1_mid_early']
            day_td2 = mid_start + int(2 * mid_duration / 3)
            if 'top_dressing_2_mid_late' in self.fertilizer_plan:
                schedule[day_td2] = self.fertilizer_plan['top_dressing_2_mid_late']
        return schedule

    def get_daily_advice(self, days_sown):
        weather_service = self.WeatherService(latitude=28.97, longitude=77.02)
        weather_data = weather_service._get_weather_data()
        et0 = self._calculate_et0(weather_data)
        rainfall_mm = weather_data['PRECTOTCORR']
        kc, stage, root_depth_m = self._get_daily_params(days_sown)
        etc_mm = et0 * kc
        taw_per_meter = self.soil_props['available_water_decimal'] * 1000 
        taw_mm = taw_per_meter * root_depth_m
        raw_mm = taw_mm * MANAGEMENT_ALLOWED_DEPLETION
        self.current_soil_depletion_mm += etc_mm
        self.current_soil_depletion_mm -= rainfall_mm
        self.current_soil_depletion_mm = max(0, self.current_soil_depletion_mm)
        irrigation_needed_mm = 0
        if self.crop_name == 'Paddy (Rice)':
            interval = self.crop_data['watering_interval_days']
            if (days_sown % interval == 0) and (days_sown != 0):
                irrigation_needed_mm = 60 
        elif self.current_soil_depletion_mm > raw_mm:
            irrigation_needed_mm = self.current_soil_depletion_mm
        gross_irrigation_mm = 0
        if irrigation_needed_mm > 0:
            gross_irrigation_mm = irrigation_needed_mm / self.irrigation_efficiency
            self.current_soil_depletion_mm -= irrigation_needed_mm
            self.current_soil_depletion_mm = max(0, self.current_soil_depletion_mm)
        fertilizer_advice = self.fertilizer_schedule.get(days_sown, "No fertilizer scheduled for this day")
        return {
            'day': days_sown,
            'stage': stage,
            'rainfall_mm': round(rainfall_mm, 2),
            'etc_mm_loss': round(etc_mm, 2),
            'current_depletion_mm': round(self.current_soil_depletion_mm, 2),
            'trigger_point_mm': round(raw_mm, 2),
            'irrigation_to_apply_mm': round(gross_irrigation_mm, 2),
            'fertilizer_advice': fertilizer_advice
        }
