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
ip_url = "http://10.107.67.24/data"


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
        # --- Fetch farmer and crop data ---
        farmer = await users_collection.find_one({"phone_number": phone})
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer not found")

        crops = farmer.get("crops", [])
        if not crops:
            raise HTTPException(status_code=400, detail="No crops found, add a new one.")

        crop_data = crops[-1]  # Use the latest crop entry

        # --- Crop & land data ---
        crop_name_raw = crop_data.get("crop_type", "")
        crop_name = crop_name_raw.strip()

        # ✅ Case-insensitive crop matching
        matched_crop_key = None
        for key in MASTER_CROP_DATABASE.keys():
            if key.lower() == crop_name.lower():
                matched_crop_key = key
                break

        if not matched_crop_key:
            raise HTTPException(status_code=400, detail=f"Crop '{crop_name}' not supported")

        crop_name = matched_crop_key  # use the standardized key

        try:
            area_acres = float(crop_data.get("land_size", 1))
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid land_size value. Must be numeric (in acres).")

        start_date_str = crop_data.get("start_date")
        if not start_date_str:
            raise HTTPException(status_code=400, detail="Missing start_date for this crop entry")

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()

        # --- Fetch soil data ---
        soil_entry = await soil_data.find_one(sort=[("_id", -1)])  # most recent soil record
        if not soil_entry:
            raise HTTPException(status_code=404, detail="No soil data found. Please analyze a soil card first.")

        soil_type = soil_entry.get("soil", "loamy").lower()
        npk_values = soil_entry.get("npk_values", {})

        if soil_type not in SOIL_WATER_PROPERTIES:
            raise HTTPException(status_code=400, detail=f"Soil type '{soil_type}' not found in water properties")

        # --- Fetch live sensor data ---
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

        # --- Initialize crop calendar ---
        calendar = CropCalendar(crop_name=crop_name, soil_type=soil_type, area_acres=area_acres)
        days_passed = (TODAY - start_date).days
        current_day_number = days_passed + 1

        if current_day_number > calendar.total_days:
            return {"message": f"Crop cycle completed for {crop_name.title()}"}

        # --- Calculate water balance ---
        stage_key, _, _, root_depth_m = calendar._get_daily_params(current_day_number)
        taw_mm = calendar._calculate_taw_mm(root_depth_m)
        initial_depletion_mm = taw_mm * (1 - MOISTURE_PERC / 100.0)
        calendar.current_soil_depletion_mm = initial_depletion_mm

        # --- Simulate past days for realistic state ---
        for d in range(1, current_day_number):
            calendar.get_daily_advice(d, 30.0, 77.0)

        # --- Generate 31-day forecast ---
        forecast = []
        for i in range(31):
            day_num = current_day_number + i
            date_iter = TODAY + timedelta(days=i)
            if day_num > calendar.total_days:
                break

            advice = calendar.get_daily_advice(
                day_num,
                30.0,
                77.0,
                TEMP_C if i == 0 else None,
                HUMIDITY_PERC if i == 0 else None
            )

            irrigation_liters = math.ceil(
                advice['irrigation_to_apply_mm'] * MM_TO_LITERS_PER_ACRE * area_acres
            )

            forecast.append({
                "date": str(date_iter),
                "stage": advice["stage"],
                "current_depletion_mm": advice["current_depletion_mm"],
                "trigger_point_mm": advice["trigger_point_mm"],
                "irrigation_mm": advice["irrigation_to_apply_mm"],
                "irrigation_liters": irrigation_liters,
                "fertilizer": _format_fertilizer_advice(advice["fertilizer_advice"])
            })

        # --- Return full simulation result ---
        return {
            "phone_number": phone,
            "crop_name": crop_name.title(),
            "soil_type": soil_type.title(),
            "area_acres": area_acres,
            "npk_values": npk_values,
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


# ============================================================
# ✅ Helper function for fertilizer display
# ============================================================
def _format_fertilizer_advice(advice):
    if isinstance(advice, str):
        return advice
    parts = []
    if advice.get('urea_kg', 0) > 0:
        parts.append(f"Urea: {advice['urea_kg']:.2f} kg")
    if advice.get('dap_kg', 0) > 0:
        parts.append(f"DAP: {advice['dap_kg']:.2f} kg")
    if advice.get('mop_kg', 0) > 0:
        parts.append(f"MOP: {advice['mop_kg']:.2f} kg")
    note = advice.get('note')
    if note:
        parts.append(f"({note})")
    return " | ".join(parts) if parts else "No fertilizer scheduled"
