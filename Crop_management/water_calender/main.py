from crop_models import CropCalendar
from config import MASTER_CROP_DATABASE, SOIL_WATER_PROPERTIES, MM_TO_LITERS_PER_ACRE, TODAY, FERTILIZER_COMPOSITION
from datetime import datetime, timedelta
import sys
import math
import json 


SIMULATION_LAT = 30.0 
SIMULATION_LON = 77.0

def get_sensor_data_json():
    """Fetches the JSON data string (simulated hardware data)."""
   
    json_string = '{"temperature_C":27.1,"humidity_%":49,"soil_moisture_%":48}'
    return json.loads(json_string) 

def format_fertilizer_advice(advice):
    """Converts the fertilizer dose dictionary into a readable string."""
    if isinstance(advice, str): return advice
    output = []
    if advice.get('urea_kg', 0) > 0: output.append(f"Urea: {advice['urea_kg']:.2f} kg")
    if advice.get('dap_kg', 0) > 0: output.append(f"DAP: {advice['dap_kg']:.2f} kg")
    if advice.get('mop_kg', 0) > 0: output.append(f"MOP: {advice['mop_kg']:.2f} kg")
    note = advice.get('note', '')
    if note: output.append(f"({note})")
    return " | ".join(output) if output else "No fertilizer scheduled for this day"

def mm_to_liters_for_area(mm_value, area_acres):
    return mm_value * MM_TO_LITERS_PER_ACRE * area_acres

def run_calendar_simulation():
    print("--- 🌾 CropDrop Advisor CLI (Final Clean) ---")
    
    try:
       
        json_data = get_sensor_data_json() 
        
        TEMP_C = json_data.get("temperature_C")
        HUMIDITY_PERC = json_data.get("humidity_%")
        MOISTURE_PERC_FROM_SENSOR = json_data.get("soil_moisture_%")
        
        if MOISTURE_PERC_FROM_SENSOR is None: raise ValueError("Soil moisture data missing from JSON.")

        print(f"✅ Sensor Data Loaded: Temp={TEMP_C}°C, Humidity={HUMIDITY_PERC}%, Moisture={MOISTURE_PERC_FROM_SENSOR}%")
     
        CROP_NAME = input("1. Enter Crop Name: ").strip().title()
        if CROP_NAME not in MASTER_CROP_DATABASE: raise ValueError(f"Crop '{CROP_NAME}' data is missing.")
            
        SOIL_TYPE = input(f"2. Enter Soil Type (e.g., loamy, clayey): ").strip().lower()
        if SOIL_TYPE not in SOIL_WATER_PROPERTIES: raise ValueError(f"Soil type '{SOIL_TYPE}' data is missing.")
            
        AREA_ACRES = float(input("3. Enter Field Area (in Acres): "))
        
        sowing_date = datetime.strptime(input("4. Enter Sowing Date (YYYY-MM-DD): "), '%Y-%m-%d').date()
        if sowing_date > TODAY: raise ValueError("Sowing Date cannot be after today's date.")
        
    except Exception as e:
        print(f"Error while taking input or loading JSON: {e}", file=sys.stderr)
        return
        
    try:
      
        calendar = CropCalendar(crop_name=CROP_NAME, soil_type=SOIL_TYPE, area_acres=AREA_ACRES)
        
        days_passed = (TODAY - sowing_date).days
        current_day_number = days_passed + 1 
        
        if current_day_number > calendar.total_days:
            print(f"🚨 Crop Cycle ({calendar.total_days} days) completed on {sowing_date + timedelta(days=calendar.total_days - 1)}. No advice needed.")
            return

        stage_key, _, _, root_depth_m = calendar._get_daily_params(current_day_number)
        taw_mm = calendar._calculate_taw_mm(root_depth_m)
        
        initial_depletion_mm = taw_mm * (1 - MOISTURE_PERC_FROM_SENSOR / 100.0)
        calendar.current_soil_depletion_mm = initial_depletion_mm
        
        print(f"Initial Soil Moisture Set: **{MOISTURE_PERC_FROM_SENSOR:.2f}%** (Depletion: **{initial_depletion_mm:.2f} mm** of {taw_mm:.2f} mm TAW)")
      
        lat, lon = SIMULATION_LAT, SIMULATION_LON
        
        print("💡 Simulating past days to update schedule status...")
        for day_num_sim in range(1, current_day_number):
            calendar.get_daily_advice(day_num_sim, lat, lon) 
        
        print(f"Current Soil Depletion Status (after simulation): **{calendar.current_soil_depletion_mm:.2f} mm**")
      
        print("="*80)
        print(f"Season's Fertilizer Plan (Fixed Schedule for {AREA_ACRES:.2f} Acres):")
       
        fertilizer_schedule = calendar.crop_data.get('npk_schedule_per_acre', {})
        for day, npk_dose in sorted(fertilizer_schedule.items()):
           
            k_req = npk_dose['k']; p_req = npk_dose['p']; n_req = npk_dose['n']; comp = FERTILIZER_COMPOSITION
            mop_kg_acre = k_req / comp['mop']['k'] if comp['mop']['k'] > 0 else 0
            dap_kg_acre = p_req / comp['dap']['p'] if comp['dap']['p'] > 0 else 0
            n_from_dap = dap_kg_acre * comp['dap']['n']
            urea_kg_acre = max(0, n_req - n_from_dap) / comp['urea']['n']
            
            final_dose = {
                'urea_kg': round(urea_kg_acre * AREA_ACRES, 2),
                'dap_kg': round(dap_kg_acre * AREA_ACRES, 2),
                'mop_kg': round(mop_kg_acre * AREA_ACRES, 2),
                'note': npk_dose.get('note', 'Scheduled Split')
            }
            
            scheduled_date = sowing_date + timedelta(days=day - 1)
            formatted_dose = format_fertilizer_advice(final_dose)
            print(f"  > Day {day} ({scheduled_date}): **{formatted_dose}**")
        
        print("-" * 80)
      
        print(f"--- 31-Day Management Calendar from {TODAY} ---")
        
        for i in range(31): 
            day_num_final = current_day_number + i
            current_date = TODAY + timedelta(days=i)
            
            if day_num_final > calendar.total_days: break
          
            temp = TEMP_C if i == 0 else None
            humidity = HUMIDITY_PERC if i == 0 else None
            
            advice = calendar.get_daily_advice(day_num_final, SIMULATION_LAT, SIMULATION_LON, temp, humidity)
            
            is_irrigation_day = advice['irrigation_to_apply_mm'] > 0
            fertilizer_output = format_fertilizer_advice(advice['fertilizer_advice'])
            irrigation_liters = math.ceil(mm_to_liters_for_area(advice['irrigation_to_apply_mm'], AREA_ACRES))
            
            print(f"\n📅 DATE: {current_date.strftime('%Y-%m-%d, %a')} (Day {day_num_final} / Stage: {advice['stage']})")
         
            print(f"  💧 WATER Status: Current Depletion **{advice['current_depletion_mm']:.2f} mm**, Irrigation Trigger **{advice['trigger_point_mm']:.2f} mm**.")

            if is_irrigation_day:
                print(f"  ✅ ACTION: **Irrigation** is required. Apply **{advice['irrigation_to_apply_mm']:.2f} mm** (approx. **{irrigation_liters:,} Liters**).")
            else:
                print(f"  ❌ ACTION: **Irrigation** is not required.")
          
            if "No fertilizer" not in fertilizer_output:
                print(f"  🌾 FERTILIZER DOSE ({AREA_ACRES:.2f} Acres): **{fertilizer_output}**")
            else:
                print(f"  🌾 FERTILIZER DOSE: Not scheduled.")
                
        print("\n--- Calendar End ---")
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        
if __name__ == "__main__":
    run_calendar_simulation()
