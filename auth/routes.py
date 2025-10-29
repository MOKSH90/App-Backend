from fastapi import APIRouter, HTTPException, Header, Depends
from auth.models import RegisterUser, LoginUser, UserProfile, Location
from auth.database import users_collection
from auth.jwt import create_access_token, verify_token
from typing import Optional
router = APIRouter()


# -------------------------
# Helper function
# -------------------------


async def check_existing_user(phone: str) -> None:
    """Check if phone already exists in DB and raise error if it does."""
    existing_user = await users_collection.find_one({"phone": phone})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists.")

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try: 
        token_type, token = authorization.split()
        if token_type.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid token type")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
    phone = verify_token(token)
    user = await users_collection.find_one({"phone": phone})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# -------------------------
# Routes
# -------------------------
@router.post("/register/")
async def register(user: RegisterUser):
    await check_existing_user(user.phone)

    # Build user document (only name + phone)
    new_user = {
        "name": user.name,
        "phone": user.phone,
    }

    # Insert into MongoDB
    result = await users_collection.insert_one(new_user)
    return {"message": "User registered successfully", "id": str(result.inserted_id)}


@router.post("/login")
async def login(user: LoginUser):
    existing_user = await users_collection.find_one({"phone": user.phone})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    access_token = create_access_token(data={"sub": existing_user["phone"]})

    # No password check (future: OTP can be added here)
    return {"message": f"Welcome {existing_user['name']}, login successful!", "access_token": access_token}


@router.get("/profile/{phone}", response_model=UserProfile)
async def get_profile(phone: str, current_user: dict = Depends(get_current_user)):
    if current_user["phone"] != phone:
        raise HTTPException(status_code=403, detail="Access forbidden")

    profile = {
        "name": current_user.get("name"),
        "phone": current_user.get("phone")
    }

    

    return UserProfile(**profile)
