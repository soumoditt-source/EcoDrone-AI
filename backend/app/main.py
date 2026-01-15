from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.ml.pit_detector import detect_pits
from app.ml.classifier import analyze_survival_at_pits
from app.ml.registration import register_images
import cv2
import numpy as np

app = FastAPI(title="EcoDrone AI API", description="Backend for Afforestation Monitoring", version="1.0.0")

# CORS setup for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "EcoDrone AI Backend is Running. Built by Soumoditya Das."}

@app.post("/analyze")
async def analyze_patch(
    op1_image: UploadFile = File(...),
    op3_image: UploadFile = File(...)
):
    """
    Main analysis endpoint.
    1. Detects pits in OP1.
    2. Registers OP3 to OP1.
    3. Classifies survival at pit locations.
    """
    try:
        # Read images
        op1_bytes = await op1_image.read()
        op3_bytes = await op3_image.read()
        
        # 1. Detect Pits (OP1)
        # Returns list of {x, y, r}
        pits = detect_pits(op1_bytes)
        
        if not pits:
            return {"status": "error", "message": "No pits detected in OP1 image."}

        # 2. Register Images (Align OP3 to OP1)
        # Returns numpy array or None
        registered_op3 = register_images(op1_bytes, op3_bytes)
        
        # Fallback if registration fails (e.g., specific features not found, or already aligned)
        image_to_analyze = registered_op3 if registered_op3 is not None else op3_bytes
        registration_status = "success" if registered_op3 is not None else "failed_fallback_to_raw"

        # 3. Analyze Survival (OP3)
        survival_stats = analyze_survival_at_pits(image_to_analyze, pits)
        
        return {
            "status": "success",
            "registration": registration_status,
            "total_pits": len(pits),
            "survival_rate": survival_stats.get("rate", 0),
            "dead_count": survival_stats.get("dead", 0),
            "details": survival_stats.get("details", [])
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
