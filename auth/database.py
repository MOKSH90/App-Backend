from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# Password hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()
# MongoDB connection (local or Atlas)
# Prefer environment variables; fall back to sensible local defaults
MONGO_URI = os.getenv("MONGO_DB_URI")

client = AsyncIOMotorClient(MONGO_URI)
DB_NAME = "farmerappdb"
# client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Enable TLS only for Atlas (mongodb+srv) or when explicitly requested
# use_tls = MONGO_URI.startswith("mongodb+srv://") or os.getenv("MONGO_TLS", "false").lower() == "true"

# if use_tls:
#     client = AsyncIOMotorClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
# else:
#     client = AsyncIOMotorClient(MONGO_URI)


users_collection = db["users"]
cart_items = db["cart"]


# Helper to format MongoDB user document
# def user_helper(user) -> dict:
#     return {
#         "id": str(user.get("_id")),
#         "name": user.get("name"),
#         "phone": user.get("phone"),
#         "email": user.get("email"),
#         "password": user.get("password"),  
#         "location": user.get("location"),
#         "land_size": user.get("land_size"),
#     }