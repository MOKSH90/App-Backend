

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.routes import router as auth_router
from chatbot.routes import router as chatbot_router
from weather.routes import router as weather_router
from image_analysis.routes import router as image_router
from micro_calculator.routes import router as micro_router
from fastapi.staticfiles import StaticFiles
from Cart.routes import router as cart_router
from Crop_management.routes import router as crop_router
from Market.routes import router as market_router 
from scan_soilcard.routes import app as soil_card_router



app = FastAPI()

app.mount("/uploadvoices", StaticFiles(directory="uploadvoices"), name="uploadvoices")
app.mount("/uploadimages", StaticFiles(directory="uploadimages"), name="uploadimages")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(chatbot_router, prefix="/chat", tags=["chat"])
app.include_router(weather_router, prefix="/weather", tags=["weather"])
app.include_router(image_router, prefix="/image-analysis", tags=["image-analysis"])
app.include_router(micro_router, prefix="/micro-calculator", tags=["calculator"])
app.include_router(cart_router, prefix="/cart", tags=["cart"])
app.include_router(crop_router, prefix="/crop", tags=["crop"])
app.include_router(market_router, prefix="/farmer", tags=["Farmer Price Tracker"])
app.include_router(soil_card_router, prefix="/soil-card", tags=["Soil card analysis"])

@app.get("/")
async def root():
    return {"message": "Farmer Chatbot Backend is running"}