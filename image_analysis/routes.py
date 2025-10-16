from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.database import db
import traceback
import datetime
import shutil
import uuid
import time
import asyncio
from image_analysis.prediction import model_predict
from image_analysis.voice_helper import generate_voice, clean_label_for_voice
from chatbot.app import get_gemini_response
import os

UPLOAD_DIR = "uploadimages"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

async def save_analysis_to_db(analysis_data: dict):
    """Async helper to save analysis to MongoDB."""
    try:
        await db["image_analyses"].insert_one(analysis_data)
        print("✅ Analysis saved to DB")
    except Exception as e:
        print(f"❌ DB save error: {e}")

@router.post("/analyze")
async def analyze_image_endpoint(
    request: Request, 
    file: UploadFile = File(...), 
    voice: bool = Query(True, description="Generate voice?"), 
    lang: str = Query("hi", description="Language: 'hi' for Hinglish, 'en' for English, 'pa' for Punjabi")
):
    start_time = time.time()
    try:
        # ✅ Fix: Content type + extension check
        allowed_types = ["image/jpeg", "image/png"]
        allowed_exts = [".jpg", ".jpeg", ".png"]

        ext = os.path.splitext(file.filename)[1].lower()
        if (file.content_type not in allowed_types) and (ext not in allowed_exts):
            raise HTTPException(status_code=400, detail="Only JPEG or PNG images are supported")

        filename = f"temp_{uuid.uuid4().hex}_{file.filename}"
        image_path = os.path.join(UPLOAD_DIR, filename)

        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        upload_end = time.time()
        print(f"⏱️ Upload time: {upload_end - start_time:.2f}s")

        # Run prediction in background thread
        analysis_start = time.time()
        analysis_result = await asyncio.to_thread(model_predict, image_path)
        analysis_end = time.time()
        print(f"⏱️ Model prediction time: {analysis_end - analysis_start:.2f}s")

        # Check if prediction succeeded
        if 'predicted_class' not in analysis_result:
            raise HTTPException(status_code=400, detail=f"Image analysis failed: {analysis_result.get('cause', 'Unknown error')}")

        # Clean disease name for natural language
        cleaned_result = clean_label_for_voice(analysis_result['predicted_class'])

        # Language mapping for style (force transliteration in English letters)
        lang_map = {
            'hi': 'Hinglish (write Hindi in English letters, e.g. "dawa lagao, paani do")',
            'hinglish': 'Hinglish (write Hindi in English letters, not Devanagari)',
            'en': 'English',
            'pa': 'Punjabi (write Punjabi in English letters, not Gurmukhi)'
        }
        user_lang = lang.lower()
        prompt_lang = lang_map.get(user_lang, 'English')

        # Build summary text (English for reference)
        summary = (
            f"This leaf is affected by {cleaned_result}. "
            f"Cause: {analysis_result['cause']}. "
            f"Treatment: {analysis_result['cure']}."
        )

        # Craft prompt for Gemini (force transliteration)
        detailed_prompt = (
            f"Briefly describe {cleaned_result} disease in {prompt_lang}. "
            f"Do not use native Hindi or Punjabi script, only English letters. "
            f"Explain what it is, treatment, cure, and fertilizer suggestions. "
            f"Keep it concise, under 80 words."
        )
        gemini_start = time.time()
        detailed_info = get_gemini_response(detailed_prompt)
        gemini_end = time.time()
        print(f"⏱️ Gemini API time: {gemini_end - gemini_start:.2f}s")

        # Generate voice (optional)
        voice_filename = None
        if voice:
            voice_start = time.time()
            voice_filename = generate_voice(detailed_info, lang=user_lang)  # Now safe with transliteration
            voice_end = time.time()
            print(f"⏱️ Voice generation time: {voice_end - voice_start:.2f}s")
        else:
            print("⏱️ Voice generation skipped (voice=false)")

        # Prepare DB data
        analysis_data = {
            "filename": filename,
            "full_path": image_path,
            "analysis_result": analysis_result,
            "summary_text": summary,
            "detailed_info": detailed_info,
            "voice_file": voice_filename,
            "user_lang": user_lang,
            "timestamp": datetime.datetime.now()
        }

        # Save to DB in background
        asyncio.create_task(save_analysis_to_db(analysis_data))

        total_time = time.time() - start_time
        print(f"⏱️ Total endpoint time: {total_time:.2f}s")

        return {
            "filename": filename,
            "image_url": f"/uploadimages/{filename}",
            "analysis_result": analysis_result,
            "summary_text": summary,
            "detailed_info": detailed_info,
            "voice_url": f"/uploadvoices/{voice_filename}" if voice_filename else None,
            "timestamp": str(datetime.datetime.now())
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in /analyze: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/dashboard", response_class=HTMLResponse)
async def image_analysis_dashboard(request: Request):
    try:
        analyses = await db["image_analyses"].find().sort("timestamp", -1).to_list(length=10)
        analyses = [
            {
                "filename": analysis["filename"],
                "image_url": f"/uploadimages/{analysis['filename']}",
                "analysis_result": analysis["analysis_result"],
                "detailed_info": analysis.get("detailed_info", "No detailed info available"),
                "timestamp": str(analysis["timestamp"])
            }
            for analysis in analyses
        ]
        return templates.TemplateResponse("image_dashboard.html", {"request": request, "analyses": analyses})
    except Exception as e:
        print(f"Error in /dashboard: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
