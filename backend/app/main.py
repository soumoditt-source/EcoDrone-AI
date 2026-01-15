from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.ml.pit_detector import detect_pits
from app.ml.classifier import analyze_survival_at_pits
from app.ml.registration import register_images
import cv2
import numpy as np
import io

# ==========================================
# EcoDrone AI Backend - "The Brain"
# Built by Soumoditya Das for Kshitij 2026
# ==========================================

app = FastAPI(
    title="EcoDrone AI API", 
    description="High-Performance Afforestation Monitoring System", 
    version="1.0.0",
    root_path="/api" # CRITICAL: Forces FastAPI to ignore the /api prefix in Vercel routes
)

# Enable CORS (Cross-Origin Resource Sharing)
# This allows our React Frontend (running on a different port) to talk to this Backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the Vercel domain!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {
        "message": "EcoDrone AI Systems Online. Ready for Analysis.",
        "author": "Soumoditya Das"
    }

@app.post("/analyze")
async def analyze_patch(
    op1_image: UploadFile = File(...),
    op3_image: UploadFile = File(...)
):
    import time
    start_time = time.time()
    
    try:
        print(f"[-] Processing Request: {op1_image.filename}")
        
        op1_bytes = await op1_image.read()
        op3_bytes = await op3_image.read()
        
        # 1. Detect Pits (OP1)
        pits = detect_pits(op1_bytes)
        
        if not pits:
            return {
                "status": "partial_error", 
                "message": "No pits detected in OP1. High probability of bad image contrast."
            }

        # 2. Register Images
        # Multi-pass registration strategy for competition accuracy
        registered_op3 = register_images(op1_bytes, op3_bytes)
        
        registration_status = "success" if registered_op3 is not None else "gps_fallback"
        image_to_analyze = registered_op3 if registered_op3 is not None else op3_bytes 

        # 3. Analyze Survival
        survival_stats = analyze_survival_at_pits(image_to_analyze, pits)
        
        exec_time = round(time.time() - start_time, 2)
        print(f"[+] Total Processing Time: {exec_time}s")

        return {
            "status": "success",
            "metrics": {
                "processing_time_sec": exec_time,
                "registration": registration_status,
                "total_pits": len(pits),
                "survival_rate": round(survival_stats.get('rate', 0), 2),
                "dead_count": survival_stats.get('dead', 0)
            },
            "casualties": [
                {"id": i, "x": p['x'], "y": p['y'], "conf": p['confidence']} 
                for i, p in enumerate(survival_stats.get('details', [])) 
                if p['status'] == 'dead'
            ],
            "raw_details": survival_stats.get("details", [])
        }
        
    except Exception as e:
        # Catch-all for robust error handling
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Processing Error: {str(e)}")
