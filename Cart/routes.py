from fastapi import APIRouter, HTTPException
from Cart.models import Product
from auth.database import cart_items, users_collection

router = APIRouter()

@router.post("/add_cart")
async def addCart(phone: str, item: Product):
    existing_user = await users_collection.find_one({"phone": phone})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing_cart = await cart_items.find_one({"phone": phone})
    if existing_cart:
        # Check if product with the same name already exists in cart
        for cart_item in existing_cart["items"]:
            if cart_item["name"] == item.name:
                cart_item["quantity"] += item.quantity
                await cart_items.update_one(
                    {"phone": phone},
                    {"$set": {"items": existing_cart["items"]}}
                )
                return {"message": "Cart updated successfully!"}
        
        # If not in cart, append new product
        existing_cart["items"].append(item.model_dump())
        await cart_items.update_one(
            {"phone": phone},
            {"$set": {"items": existing_cart["items"]}}
        )
        return {"message": f"{item.name} added to cart successfully!"}
    
    # Create new cart if not exists
    new_cart = {
        "phone": phone,
        "items": [item.model_dump()]
    }
    await cart_items.insert_one(new_cart)
    return {"message": f"{item.name} added to cart successfully!"}

@router.get("/get_cart")
async def get_cart(phone: str):
    existing_user = await users_collection.find_one({"phone": phone})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    cart = await cart_items.find_one({"phone": phone})
    if not cart or "items" not in cart:
        return {"items": []}
    
    return {"items": cart["items"]}
