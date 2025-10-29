from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional

class Product(BaseModel):
    name: str
    price: float
    farm:str
    rating: str
    image_url: str
    quantity: int = Field(..., ge=1, le=5)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

