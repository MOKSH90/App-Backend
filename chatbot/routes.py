from fastapi import APIRouter, HTTPException, UploadFile, File
import traceback
from chatbot.models import ChatRequest
from auth.database import db  
import datetime
import shutil
import uuid
import os
from chatbot.app import get_gemini_response, transcribe_audio
from image_analysis.voice_helper import generate_voice  

# -------------------------
# Setup
# -------------------------
router = APIRouter()

UPLOAD_AUDIO_DIR = "uploadaudio"
UPLOAD_VOICE_DIR = "uploadvoices"

os.makedirs(UPLOAD_AUDIO_DIR, exist_ok=True)
os.makedirs(UPLOAD_VOICE_DIR, exist_ok=True)


# -------------------------
# Helpers
# -------------------------
def get_general_ai_response(prompt: str) -> str:
    """Call Gemini API and return AI response text."""
    return get_gemini_response(prompt)


async def save_chat_to_db(chat_data: dict):
    """Save chat history into MongoDB."""
    try:
        await db["chat_history"].insert_one(chat_data)
        print("✅ Chat saved to DB")
    except Exception as e:
        print(f"❌ DB save error: {e}")


# -------------------------
# Routes
# -------------------------
@router.post("/general")
async def general_chat(request: ChatRequest):
    """General text chat with Gemini AI."""
    try:
        response = get_general_ai_response(request.prompt)

        # Save chat history
        await db["chat_history"].insert_one({
            "type": "general",
            "prompt": request.prompt,
            "response": response,
            "timestamp": datetime.datetime.now()
        })

        return {"response": response}
    except Exception:
        print(f"Error in /chat/general: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/voice_chat")
async def voice_chat(audio: UploadFile = File(..., description="Audio file (WAV/MP3, <60s)")):
    """Voice chat: speech → text → AI response → speech."""
    try:
        if audio.content_type not in ["audio/wav", "audio/mpeg", "audio/mp3"]:
            raise HTTPException(status_code=400, detail="Only WAV/MP3 audio supported")

        # Save uploaded audio temporarily
        filename = f"temp_audio_{uuid.uuid4().hex}.{audio.filename.split('.')[-1]}"
        audio_path = os.path.join(UPLOAD_AUDIO_DIR, filename)

        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        # Transcribe audio
        with open(audio_path, "rb") as f:
            audio_content = f.read()
        transcript, detected_lang = transcribe_audio(audio_content)

        if not transcript or "failed" in transcript.lower():
            raise HTTPException(status_code=400, detail="Audio transcription failed. Please try clearer speech.")

        print(f"🔍 Transcribed: '{transcript}' (Detected lang: {detected_lang})")

        # AI response
        response = get_general_ai_response(transcript)

        # Generate voice reply
        voice_filename = generate_voice(
            response,
            lang=detected_lang.split('-')[0],
            use_ssml=True,
            custom_rate=0.95
        )

        # Move generated file into static folder
        voice_file_path = os.path.join(UPLOAD_VOICE_DIR, voice_filename)
        if os.path.exists(voice_filename):
            shutil.move(voice_filename, voice_file_path)

        # Save chat history
        chat_data = {
            "type": "voice_chat",
            "transcript": transcript,
            "detected_lang": detected_lang,
            "response": response,
            "voice_file": voice_filename,
            "timestamp": datetime.datetime.now()
        }
        await save_chat_to_db(chat_data)

        # Clean up temp audio
        os.remove(audio_path)

        return {
            "transcript": transcript,
            "detected_language": detected_lang,
            "response_text": response,
            "voice_url": f"/uploadvoices/{voice_filename}" if voice_filename else None,
            "timestamp": str(datetime.datetime.now())
        }

    except Exception:
        print(f"Error in /voice_chat: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")
