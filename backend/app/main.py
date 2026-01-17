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
        "author": "Soumoditya Das",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Vercel and monitoring"""
    import cv2
    return {
        "status": "healthy",
        "opencv_version": cv2.__version__,
        "api_version": "1.0.0"
    }

@app.post("/analyze")
async def analyze_patch(
    op1_image: UploadFile = File(...),
    op3_image: UploadFile = File(...)
):
    import time
    start_time = time.time()
    
    try:
        print(f"\n{'='*60}")
        print(f"[REQUEST] Processing: {op1_image.filename} + {op3_image.filename}")
        print(f"{'='*60}")
        
        op1_bytes = await op1_image.read()
        op3_bytes = await op3_image.read()
        
        print(f"[INFO] OP1 size: {len(op1_bytes)} bytes")
        print(f"[INFO] OP3 size: {len(op3_bytes)} bytes")
        
        # 1. Detect Pits (OP1)
        print("\n[STEP 1] Detecting pits in OP1...")
        pits = detect_pits(op1_bytes)
        
        if not pits:
            print("[WARNING] No pits detected in OP1")
            return {
                "status": "partial_error", 
                "message": "No pits detected in OP1. Please ensure the image shows clear planting pits with good contrast.",
                "metrics": {
                    "processing_time_sec": round(time.time() - start_time, 2),
                    "total_pits": 0,
                    "survival_rate": 0,
                    "dead_count": 0
                },
                "casualties": [],
                "raw_details": []
            }

        print(f"[SUCCESS] Detected {len(pits)} pits")

        # 2. Register Images
        print("\n[STEP 2] Registering OP3 to OP1...")
        registered_op3 = register_images(op1_bytes, op3_bytes)
        
        registration_status = "success" if registered_op3 is not None else "gps_fallback"
        image_to_analyze = registered_op3 if registered_op3 is not None else op3_bytes
        
        if registration_status == "success":
            print("[SUCCESS] Images aligned successfully")
        else:
            print("[WARNING] Registration failed, using raw OP3 image")

        # 3. Analyze Survival
        print("\n[STEP 3] Analyzing survival at pit locations...")
        survival_stats = analyze_survival_at_pits(image_to_analyze, pits)
        
        if "error" in survival_stats:
            raise HTTPException(status_code=500, detail=survival_stats["error"])
        
        exec_time = round(time.time() - start_time, 2)
        print(f"\n[COMPLETE] Total Processing Time: {exec_time}s")
        print(f"[RESULTS] Survival Rate: {survival_stats.get('rate', 0):.1f}%")
        print(f"{'='*60}\n")

        response = {
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
        
        # Validate response
        if not response["raw_details"]:
            print("[WARNING] No analysis details in response")
        
        return response
        
    except Exception as e:
        # Catch-all for robust error handling
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n[ERROR] Processing failed:")
        print(error_trace)
        raise HTTPException(
            status_code=500, 
            detail=f"Internal Processing Error: {str(e)}. Check server logs for details."
        )
