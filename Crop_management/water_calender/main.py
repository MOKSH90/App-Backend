
from crop_models import CropCalendar
from config import MASTER_CROP_DATABASE
from datetime import datetime, timedelta
import sys

TODAY = datetime.now().date()

def format_fertilizer_advice(advice):
    """Converts the fertilizer dose dictionary into a readable string."""
    if isinstance(advice, str):
        return advice
    output = []
 
    if advice.get('urea_kg', 0) > 0:
        output.append(f"Urea: {advice['urea_kg']} kg")
    if advice.get('dap_kg', 0) > 0:
        output.append(f"DAP: {advice['dap_kg']} kg")
    if advice.get('mop_kg', 0) > 0:
        output.append(f"MOP: {advice['mop_kg']} kg")
        
    return " | ".join(output) if output else "No fertilizer scheduled for this day"

def run_calendar_simulation():
    """Runs the main command-line interface for the crop calendar."""
    try:
       
        CROP_NAME = input("Enter Crop Name (e.g., Wheat, Maize): ")
        CROP_NAME = CROP_NAME.strip().title()
        if CROP_NAME not in MASTER_CROP_DATABASE:
            print(f"Error: Crop '{CROP_NAME}' data is missing from the database.")
            return
            
        SOIL_TYPE = input("Enter Soil Type (e.g., loamy, sandy): ")
        SOIL_TYPE = SOIL_TYPE.strip().lower()
        
        STATE = input("Enter State (e.g., UP, Punjab): ")
        STATE = STATE.strip().lower()
        
        while True:
            try:
                AREA_ACRES = float(input("Enter Field Area (in Acres): "))
                if AREA_ACRES <= 0:
                        raise ValueError
                break
            except ValueError:
                print("Invalid input. Area must be a positive number.")
                
        while True:
            START_DATE_STR = input("Enter Sowing Date (YYYY-MM-DD): ")
            try:
                sowing_date = datetime.strptime(START_DATE_STR, '%Y-%m-%d').date()
                if sowing_date > TODAY:
                    print("Sowing Date cannot be after today's date. Please enter a valid date.")
                    continue
                break
            except ValueError:
                print("Invalid format. Please use YYYY-MM-DD format.")
                
    except Exception as e:
        print(f"Error while taking input: {e}")
        return
        
    try:
       
        print("\n--- Initializing Model... ---")
        calendar = CropCalendar(
            crop_name=CROP_NAME,
            soil_type=SOIL_TYPE,
            state=STATE,
            area_acres=AREA_ACRES
        )
        
        days_passed = (TODAY - sowing_date).days
        current_day_number = days_passed + 1 
       
        if current_day_number > calendar.total_days:
            print(f"🚨 Crop Cycle ({calendar.total_days} days) completed on {sowing_date + timedelta(days=calendar.total_days - 1)}. No advice needed.")
            return

        total_days_in_crop_cycle = calendar.total_days
        
        print(f"Crop: {CROP_NAME} ({STATE}) | Area: {AREA_ACRES} Acres | Total Duration: {total_days_in_crop_cycle} days")
        print(f"Sowing Date: {sowing_date} | Current Day Number: {current_day_number}")
        print(f"Irrigation Logic: Needs-Based (Soil Water Balance)")
        print("="*80)
      
        print(f"Season's Fertilizer Plan (Doses for {AREA_ACRES} Acres):")
        for key, doses in calendar.fertilizer_plan.items():
            formatted_dose = format_fertilizer_advice(doses)

            schedule_day = next((day for day, plan in calendar.fertilizer_schedule.items() if plan == doses), None)
            
            if schedule_day is not None:
                scheduled_date = sowing_date + timedelta(days=schedule_day - 1)
             
                if isinstance(key, str):
                    plan_name = key.replace('_', ' ').title()
                else:
                    plan_name = doses.get('note', f"Scheduled Split on Day {key}")
                print(f"  > {plan_name} (Scheduled Day {schedule_day} - {scheduled_date}): {formatted_dose}")
            else:
                
                if isinstance(key, str):
                    print(f"  > {key.replace('_', ' ').title()}: {formatted_dose}")
                else:
                    print(f"  > Scheduled Day {key}: {formatted_dose}") 
        
        
        print("-" * 80)
        print("💡 Simulating past days to calculate current soil/schedule status...")
       
        for day_num_sim in range(1, current_day_number):
            calendar.get_daily_advice(day_num_sim)
            
        print(f"Current Soil Depletion Status (after simulation): {round(calendar.current_soil_depletion_mm, 2)} mm")
        print("-" * 80)
        print(f"--- 31-Day Management Calendar ---")
        
      
        for i in range(31): 
            day_num_final = current_day_number + i
            current_date = TODAY + timedelta(days=i)
           
            if day_num_final > total_days_in_crop_cycle:
            
                break
            
            
            advice = calendar.get_daily_advice(day_num_final)
            
            is_irrigation_day = advice['irrigation_to_apply_mm'] > 0
            fertilizer_output = format_fertilizer_advice(advice['fertilizer_advice'])
            is_fertilizer_day = "No fertilizer scheduled for this day" not in fertilizer_output
        
            print(f"\n📅 DATE: {current_date.strftime('%Y-%m-%d, %A')} (Day {day_num_final} / Stage: {advice['stage']})")

            if is_irrigation_day:
                print(f"  💧 IRRIGATION NEEDED: **{advice['irrigation_to_apply_mm']} mm** of water.")
            else:
                print(f"  💧 IRRIGATION NEEDED: Not required today.")
         
            if is_fertilizer_day:
                print(f"  🌾 FERTILIZER DOSE ({AREA_ACRES} Acres): **{fertilizer_output}**")
            else:
                print(f"  🌾 FERTILIZER DOSE ({AREA_ACRES} Acres): No fertilizer scheduled for this day.")
                
        print("\n--- Calendar End ---")
        
    except ValueError as e:
        print(f"ERROR: Model could not run. {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        
if __name__ == "__main__":
    run_calendar_simulation()