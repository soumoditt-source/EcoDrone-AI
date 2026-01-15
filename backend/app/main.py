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
    version="1.0.0"
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
    """
    Core Analysis Pipeline:
    1. READ: Ingest heavy drone orthomosaics.
    2. DETECT: Find pit locations in Year 1 data (OP1).
    3. REGISTER: Align Year X data (OP3) to match Year 1 geometry.
    4. CLASSIFY: Check each pit location for sapling survival (ExG Index).
    """
    try:
        # --- I/O OPTIMIZATION NOTE ---
        # For huge files (>100MB), reading into memory (await .read()) is a bottleneck.
        # In a real production scale (Azure/AWS), we would stream these to a temp file 
        # or process them in chunks. For Hackathon scale (<50MB), RAM is faster.
        
        print(f"[-] Receiving files: {op1_image.filename} & {op3_image.filename}")
        
        op1_bytes = await op1_image.read()
        op3_bytes = await op3_image.read()
        
        # 1. Detect Pits (OP1)
        # Using Hough Circle Transform tailored for 45cm pits @ 2.5cm/px
        pits = detect_pits(op1_bytes)
        
        if not pits:
            # Fallback/Corner Case: No pits found?
            # Maybe the image is too dark or empty. Return graceful error.
            return {
                "status": "partial_error", 
                "message": "No pits detected in OP1. Check image alignment or contrast."
            }

        print(f"[+] Detected {len(pits)} pits in base layer.")

        # 2. Register Images (Align OP3 to OP1)
        # Critical Step: Drones have GPS drift (~1m). SIFT fixes this.
        registered_op3 = register_images(op1_bytes, op3_bytes)
        
        # Decision Block: Did registration work?
        if registered_op3 is not None:
            image_to_analyze = registered_op3
            registration_status = "success"
            print("[+] Image Registration Successful (SIFT).")
        else:
            # Fallback: If not enough features (e.g., bare soil), use raw OP3.
            # We assume the drone GPS was 'good enough' for a rough estimate.
            image_to_analyze = op3_bytes 
            registration_status = "failed_fallback_to_raw"
            print("[!] Registration failed (low texture?). Using raw OP3.")

        # 3. Analyze Survival (OP3)
        # Check bio-indicators at every pit location.
        survival_stats = analyze_survival_at_pits(image_to_analyze, pits)
        
        print(f"[+] Analysis Complete. Survival Rate: {survival_stats.get('rate'):.1f}%")

        return {
            "status": "success",
            "registration": registration_status,
            "total_pits": len(pits),
            "survival_rate": survival_stats.get("rate", 0),
            "dead_count": survival_stats.get("dead", 0),
            "details": survival_stats.get("details", [])
        }
        
    except Exception as e:
        # Catch-all for robust error handling
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Processing Error: {str(e)}")
