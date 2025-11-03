
from fastapi import APIRouter, File, UploadFile, HTTPException
from scan_soilcard.Untitled11 import run_ocr_and_analyze 
from auth.database import soil_data

app = APIRouter()


@app.get("/")
def read_root():
    return {"status": "ok", "service": "Soil Advisor OCR API is Ready!"}


@app.post("/analyze_soil_card")
async def analyze_soil_card(file: UploadFile = File(...)):
    
    MAX_FILE_SIZE = 5 * 1024 * 1024 
    
    try:
        
        contents = await file.read()

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File size too large. Max 5MB allowed.")
     
        result = run_ocr_and_analyze(contents, file.filename)
        
        
        if "error" in result:
             raise HTTPException(status_code=500, detail=result['error'])
        
        soil_data.insert_one(result)

        return {
            "filename": file.filename,
            "message": "Analysis successful.",
            "data": result
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server processing failed: {str(e)}")
