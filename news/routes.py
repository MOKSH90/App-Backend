# news/news.py (or news/routes.py)
from fastapi import APIRouter
import requests
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

@router.get("/crop-news")
async def get_crop_news():
    api_key = os.getenv("NEWSAPI_KEY")  # Replace with your key
    # Broad query covering all crop/agriculture related topics
    query = "agriculture OR farming OR crops OR harvest OR farmer"
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}&language=en&sortBy=publishedAt&pageSize=10"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # Extract only useful fields for frontend
        articles = [
            {
                "title": a.get("title"),
                "description": a.get("description"),
                "url": a.get("url"),
                "image": a.get("urlToImage"),
                "publishedAt": a.get("publishedAt"),
                "source": a.get("source", {}).get("name")
            }
            for a in data.get("articles", [])
        ]

        return {"articles": articles}

    except Exception as e:
        return {"error": str(e), "articles": []}
