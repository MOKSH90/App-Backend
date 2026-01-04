from pydantic import BaseModel, Field
from enum import Enum
from datetime import date

class Crop_type_select(str, Enum):
    wheat = "wheat"
    corn = "corn"
    tomato = "tomato"
    potato = "potato"
    sugarcane = "sugarcane"
    paddy_rice = "paddy (rice)"
    bajra = "bajra"
    banana = "banana"
    brinjal = "brinjal"
    cabbage = "cabbage"
    cauliflower = "cauliflower"
    cotton = "cotton"
    cucumber = "cucumber"
    garlic = "garlic"
    ginger = "ginger"
    green_chilli = "green chilli"
    guava = "guava"
    jowar = "jowar"
    lemon = "lemon"
    maize = "maize"
    mango = "mango"
    mustard = "mustard"
    okra = "okra"
    onion = "onion"
    orange = "orange"
    peas = "peas"
    soyabean = "soyabean"
    sunflower = "sunflower"
    watermelon = "watermelon"

class Soil_select(str, Enum):
    alluvial = "alluvial"
    clayey = "clayey"
    loamy = "loamy"
    sandy = "sandy"
    black = "black"
    red_and_yellow = "red and yellow"
    laterite = "laterite"
    arid = "arid"
    forest = "forest"

class Add_Crops(BaseModel):
    crop_type: Crop_type_select
    land_size: float = Field(..., gt=0, description="Land area in acres")
    start_date: date