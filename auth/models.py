from pydantic import BaseModel, validator, Field
from typing import Optional


class RegisterUser(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=10)

    @validator("phone")
    def must_be_ten_digits(cls, v):
        if not v.isdigit():
            raise ValueError("Phone must contain only digits")
        return v
    

class LoginUser(BaseModel):
    phone: str


class Location(BaseModel):
    lat: float
    lon: float
    state: Optional[str] = None
    district: Optional[str] = None


class UserProfile(BaseModel):
    name: str
    phone: str
