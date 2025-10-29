from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from Market.predictor.app import FarmerPriceTracker 
from Market.predictor.mandi_api import MandiAPI
from enum import Enum

router = APIRouter()

class Crop_type_select(str, Enum):
    wheat = "Wheat"
    corn = "Corn"
    tomato = "Tomato"
    potato = "Potato"
    sugarcane = "Sugarcane"
    paddy_rice = "Paddy (Rice)"
    bajra = "Bajra"
    banana = "Banana"
    brinjal = "Brinjal"
    cabbage = "Cabbage"
    cauliflower = "Cauliflower"
    cotton = "Cotton"
    cucumber = "Cucumber"
    garlic = "Garlic"
    ginger = "Ginger"
    green_chilli = "Green Chilli"
    guava = "Guava"
    jowar = "Jowar"
    lemon = "Lemon"
    maize = "Maize"
    mango = "Mango"
    mustard = "Mustard"
    okra = "Okra"
    onion = "Onion"
    orange = "Orange"
    peas = "Peas"
    soyabean = "Soyabean"
    sunflower = "Sunflower"
    watermelon = "Watermelon"

class StateSelect(str, Enum):
    haryana = "Haryana"
    punjab = "Punjab"
    uttarpradesh = "Uttar Pradesh"
    madhyapradesh = "Madhya Pradesh"
    rajasthan = "Rajasthan"
    maharashtra = "Maharashtra"
    karnataka = "Karnataka"
    westbengal = "West Bengal"
    gujarat = "Gujarat"
    bihar = "Bihar"
    andhrapradesh = "Andhra Pradesh"
    telangana = "Telangana"
    
class FarmerRequest(BaseModel):
    state: StateSelect
    crop: Crop_type_select


@router.post("/predict")
async def predict(data: FarmerRequest):
    try:
        tracker = FarmerPriceTracker()

        # Get current price data
        price_data = tracker.api.get_current_prices(data.state, data.crop.value, tracker.predictor)

        # Get prediction data
        prediction_data = tracker.predictor.ml_price_prediction(data.state, data.crop.value)

        if not price_data and ("error" in prediction_data):
            raise HTTPException(status_code=400, detail="Prediction failed or no data available")

        # Return everything as structured JSON
        return {
            "status": "success",
            "state": data.state.value,
            "crop": data.crop.value,
            "price_data": price_data,
            "prediction_data": prediction_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/fetch-price")
async def FetchData(data: FarmerRequest):
    try: 
        api = MandiAPI()

        result = api.get_weekly_historical_data(
            state = data.state.value,
            crop = data.crop.value
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fetching failed: {str(e)}")