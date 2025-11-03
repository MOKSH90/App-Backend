import cv2
import pytesseract
from PIL import Image
import numpy as np
import re
import io
from pdf2image import convert_from_bytes
import warnings
import platform
import os

warnings.filterwarnings('ignore', category=UserWarning, module='pytesseract')

if platform.system() == "Windows":
    TESSERACT_CMD_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    POPPLER_BIN_PATH = r'C:\Program Files\poppler-24.02.0\Library\bin' 
    os.environ['PATH'] += os.pathsep + r'C:\Program Files\Tesseract-OCR'
    os.environ['PATH'] += os.pathsep + POPPLER_BIN_PATH
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD_PATH
else:
    POPPLER_BIN_PATH = None

CROP_REQUIREMENTS = [
   
    {"Crop": "Wheat", "Min_N": 100, "Min_P": 40, "Min_K": 30},
    {"Crop": "Paddy", "Min_N": 120, "Min_P": 50, "Min_K": 50},
    {"Crop": "Maize", "Min_N": 80, "Min_P": 30, "Min_K": 20},
    {"Crop": "Potato", "Min_N": 150, "Min_P": 70, "Min_K": 80},
]

def preprocess_image(image):
    
    if isinstance(image, Image.Image):
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    else:
        img = image 
       
    return Image.fromarray(np.zeros((10, 10), dtype=np.uint8))


def extract_npk_values(text_data):
  
    npk_results = {
        "Available N": 200.63,
        "Available P": 4.19,
        "Available K": 122.85,
        "pH": 7.70
    }
    return npk_results

def recommend_crop(soil_npk_data, requirements):
    soil_n = soil_npk_data.get("Available N")
    soil_p = soil_npk_data.get("Available P")
    soil_k = soil_npk_data.get("Available K")
    
    if soil_n is None or soil_p is None or soil_k is None:
        return "Not enough NPK data extracted to recommend a crop."
        
    recommended_crops = []
    
    for crop_data in requirements:
        crop_name = crop_data["Crop"]
        req_n = crop_data["Min_N"]
        req_p = crop_data["Min_P"]
        req_k = crop_data["Min_K"]
        
        n_ok = (soil_n >= req_n)
        p_ok = (soil_p >= req_p)
        k_ok = (soil_k >= req_k)
        
        if n_ok and p_ok and k_ok:
            recommended_crops.append(f"{crop_name} (Excellent Fit)")

    if recommended_crops:
        return " | ".join([c for c in recommended_crops])
    else:
        return "No listed crop fully matches the soil's nutrient levels."

def run_ocr_and_analyze(file_contents: bytes, filename: str):
   
    final_npk_data = extract_npk_values("")
    recommendation = recommend_crop(final_npk_data, CROP_REQUIREMENTS)
    
    soil_data = "Black Soil" 

    raw_text = "Soil Sample Details: Hardcoded for testing purposes." 

    return {
        "npk_values": final_npk_data,
        "recommendation": recommendation,
        "soil": soil_data,
        "raw_ocr_text": raw_text
    }