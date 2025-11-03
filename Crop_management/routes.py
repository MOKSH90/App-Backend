from fastapi import APIRouter, HTTPException
import httpx
import math
from datetime import datetime, timedelta, date

# --- Local imports ---
from Crop_management.models import Add_Crops
from auth.database import users_collection, soil_data
from Crop_management.water_calender.crop_models import CropCalendar
from Crop_management.water_calender.config import (
    MASTER_CROP_DATABASE,
    SOIL_WATER_PROPERTIES,
    MM_TO_LITERS_PER_ACRE,
    TODAY,
    FERTILIZER_COMPOSITION
)

router = APIRouter()

# Replace with your sensor endpoint
ip_url = "http://192.168.220.173/data"


# ============================================================
# ✅ Add Crop Endpoint
# ============================================================
@router.post("/add_crops")
async def Add_crop(phone: str, crop: Add_Crops):
    try:
        farmer = await users_collection.find_one({"phone_number": phone})
        crops = farmer.get("crops", []) if farmer else []

        if len(crops) >= 3:
            raise HTTPException(status_code=400, detail="You can only manage up to 3 crops at a time.")

        crop_data = crop.model_dump()
        crop_data.update({"phone_number": phone})

        # ✅ Convert date to string
        for key, value in crop_data.items():
            if isinstance(value, date):
                crop_data[key] = value.isoformat()

        # ✅ Ensure land_size is numeric
        try:
            crop_data["land_size"] = float(crop_data["land_size"])
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid land_size value. It must be numeric.")

        result = await users_collection.update_one(
            {"phone_number": phone},
            {"$push": {"crops": crop_data}},
            upsert=True
        )

        return {
            "message": "Crop added successfully!",
            "modified_count": result.modified_count
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding crop: {str(e)}")


# ============================================================
# ✅ Get All Crops Endpoint
# ============================================================
@router.get("/all_crops")
async def get_all_crops(phone: str):
    try:
        farmer = await users_collection.find_one({"phone_number": phone})
        if not farmer:
            raise HTTPException(status_code=404, detail="User not found")

        crops = farmer.get("crops", [])
        return {"phone_number": phone, "crops": crops}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching crops: {str(e)}")


# ============================================================
# ✅ Fetch Live Soil Sensor Data
# ============================================================
@router.get("/fetch_soil_details")
async def FetchSoilData():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(ip_url)
            response.raise_for_status()
            data = response.json()
            return {"source": ip_url, "soil_data": data}
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Remote error: {e}")


# ============================================================
# ✅ Utility Functions
# ============================================================
def format_fertilizer_advice(advice):
    if isinstance(advice, str):
        return advice

    output = []
    if advice.get('urea_kg', 0) > 0: output.append(f"Urea: {advice['urea_kg']:.2f} kg")
    if advice.get('dap_kg', 0) > 0: output.append(f"DAP: {advice['dap_kg']:.2f} kg")
    if advice.get('mop_kg', 0) > 0: output.append(f"MOP: {advice['mop_kg']:.2f} kg")
    note = advice.get('note', '')
    if note: output.append(f"({note})")
    return " | ".join(output) if output else "No fertilizer scheduled"


def mm_to_liters_for_area(mm_value, area_acres):
    return mm_value * MM_TO_LITERS_PER_ACRE * area_acres


# ============================================================
# ✅ Simulate Crop Growth and Forecast
# ============================================================
@router.post("/simulate_crop")
async def simulate_crop(phone: str):
    try:
        # Fetch farmer record
        farmer = await users_collection.find_one({"phone_number": phone})
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer not found")

        crops = farmer.get("crops", [])
        if not crops:
            raise HTTPException(status_code=400, detail="No crops found, add a new one first.")

        crop_data = crops[-1]  # most recent crop entry

        crop_name = crop_data.get("crop_type", "").lower()
        area_acres = float(crop_data.get("land_size", 1))

        start_date_str = crop_data.get("start_date")
        if not start_date_str:
            raise HTTPException(status_code=400, detail="Missing start_date for this crop entry")
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()

        # ✅ Fetch soil data from soil_data collection
        # ✅ Fetch latest soil data entry
        soil_record = await soil_data.find_one(sort=[("_id", -1)])
        if not soil_record:
            raise HTTPException(status_code=404, detail="No soil data found. Please analyze your soil card first.")

        # Extract soil info
        soil_type = soil_record.get("soil", "loamy").lower()
        npk_values_obj = soil_record.get("npk_values", {})

        npk_values = {
            "Available_N": npk_values_obj.get("Available N", 0.0),
            "Available_P": npk_values_obj.get("Available P", 0.0),
            "Available_K": npk_values_obj.get("Available K", 0.0),
            "pH": npk_values_obj.get("pH", 0.0)
        }


        # ✅ Validate soil type
        if soil_type not in SOIL_WATER_PROPERTIES:
            raise HTTPException(status_code=400, detail=f"Soil type '{soil_type}' not supported")

        # ✅ Validate crop type
        if crop_name not in MASTER_CROP_DATABASE:
            raise HTTPException(status_code=400, detail=f"Crop '{crop_name}' not supported")

        # ✅ Fetch sensor data
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                sensor_response = await client.get(ip_url)
                sensor_response.raise_for_status()
                sensor_data = sensor_response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch sensor data: {e}")

        TEMP_C = sensor_data.get("temperature_C")
        HUMIDITY_PERC = sensor_data.get("humidity_%")
        MOISTURE_PERC = sensor_data.get("soil_moisture_%")

        if any(v is None for v in [TEMP_C, HUMIDITY_PERC, MOISTURE_PERC]):
            raise HTTPException(status_code=400, detail="Incomplete sensor data received")

        # ✅ Initialize CropCalendar
        calendar = CropCalendar(crop_name=crop_name, soil_type=soil_type, area_acres=area_acres)
        days_passed = (TODAY - start_date).days
        current_day_number = days_passed + 1

        if current_day_number > calendar.total_days:
            return {"message": f"Crop cycle completed for {crop_name}"}

        # ✅ Calculate water balance
        stage_key, _, _, root_depth_m = calendar._get_daily_params(current_day_number)
        taw_mm = calendar._calculate_taw_mm(root_depth_m)
        initial_depletion_mm = taw_mm * (1 - MOISTURE_PERC / 100.0)
        calendar.current_soil_depletion_mm = initial_depletion_mm

        # ✅ Simulate previous days
        for d in range(1, current_day_number):
            calendar.get_daily_advice(d, 30.0, 77.0)

        # ✅ 31-day forecast
        forecast = []
        for i in range(31):
            day_num = current_day_number + i
            date_val = TODAY + timedelta(days=i)
            if day_num > calendar.total_days:
                break

            advice = calendar.get_daily_advice(
                day_num, 30.0, 77.0,
                TEMP_C if i == 0 else None,
                HUMIDITY_PERC if i == 0 else None
            )
            irrigation_liters = math.ceil(mm_to_liters_for_area(advice['irrigation_to_apply_mm'], area_acres))

            forecast.append({
                "date": str(date_val),
                "stage": advice["stage"],
                "current_depletion_mm": advice["current_depletion_mm"],
                "trigger_point_mm": advice["trigger_point_mm"],
                "irrigation_mm": advice["irrigation_to_apply_mm"],
                "irrigation_liters": irrigation_liters,
                "fertilizer": format_fertilizer_advice(advice["fertilizer_advice"])
            })

        return {
            "phone_number": phone,
            "crop_name": crop_name,
            "soil_type": soil_type,
            "npk_values": npk_values,
            "area_acres": area_acres,
            "start_date": start_date_str,
            "sensor_data": sensor_data,
            "forecast_start": str(TODAY),
            "forecast_days": len(forecast),
            "forecast": forecast
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running simulation: {str(e)}")
