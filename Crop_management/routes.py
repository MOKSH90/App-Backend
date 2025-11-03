from fastapi import APIRouter, HTTPException
import httpx
from Crop_management.models import Add_Crops
from auth.database import users_collection

import sys
from enum import Enum
app = APIRouter()

router = APIRouter()
ip_url = "http://192.168.220.173/data"

@router.post("/add_crops")
async def Add_crop(phone: str, crop: Add_Crops):
    try:

        farmer = await users_collection.find_one({"phone_number": phone})
        crops = farmer.get("crops", []) if farmer else []

        if len(crops) >= 3:
            raise HTTPException(status_code=400, detail="You can only manage upto 3 crops at a time.")
        
        crop_data = crop.model_dump()
        crop_data.update({"phone_number": phone})

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
    
@router.get("/all_crops")
async def get_all_crops(phone: str):
    try:
        farmer = await users_collection.find_one({"phone_number": phone})
        if not farmer:
            raise HTTPException(status_code=404, detail="User not found")
        
        crops = farmer.get("crops", [])
        return {"phone_number": phone, "crops": crops}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching the crops: {str(e)}")

@router.get("/fetch_soil_details")
async def FetchSoilData():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(ip_url)
            response.raise_for_status()
            data = response.json()
            return{"source": ip_url, "soil_data": data}
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Remote error: {e}")
    


