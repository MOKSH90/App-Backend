from fastapi import APIRouter, HTTPException
from Crop_management.models import Add_Crops
from auth.database import users_collection

router = APIRouter()

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