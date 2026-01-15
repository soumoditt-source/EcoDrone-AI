# EcoDrone AI
### Built by Soumoditya Das (soumoditt@gmail.com)
**Kshitij 2026: Build with Gemini Hackathon Submission**

## Overview
EcoDrone AI is a production-ready Web Application designed to revolutionize afforestation monitoring using Drone Imagery and Computer Vision. It automates the analysis of sapling survival rates by comparing "Pit" locations (Year 1, OP1) with current sapling growth (Year 1/2/3, OP3).

## Key Features
- **Zero-Dependency Deployment**: Custom Vanilla CSS "Glassmorphism" UI for premium aesthetics without heavy frameworks.
- **Deep Research ML Pipeline**: 
  - **Pit Detection**: Hough Circle Transform tailored for 45cm pits at 2.5cm/px resolution.
  - **Temporal Registration**: SIFT + RANSAC for sub-meter alignment of multi-year drone surveys.
  - **Sapling Classification**: Excess Green Index (ExG) + MobileNetV3/YOLOv8-ready architecture.
- **Interactive Visualization**: Leaflet-based map with "Time Travel" slider and Casualty Heatmaps.

## Methodology (Deep Research)
1. **Pit Detection**: We identify the initial planting grid using geometric feature extraction (Hough Circles) on OP1 images, filtering for the 45cm diameter variance expected from manual labor.
2. **Registration**: To counter GPS drift (±1m), OP3 orthomosaics are warped to match OP1 coordinate space using feature matching (SIFT).
3. **Classification**: 
   - **Alive**: High ExG index (>20) indicating chlorophyll presence.
   - **Dead**: Low ExG or bare soil texture.
   - **Bio-Alignment**: Methodology aligned with **DeadTrees.Earth** (University of Freiburg) for remote sensing of mortality.
   - **Confidence**: Probabilistic scoring based on texture and color variance.

## Tech Stack
- **Frontend**: React, Vite, Framer Motion, Leaflet, Vanilla CSS (Variables).
- **Backend**: Python, FastAPI, OpenCV, PyTorch.

## How to Run
1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn app.main:app --reload
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. Open `http://localhost:5173`

## Author
**Soumoditya Das**  
[soumoditt@gmail.com](mailto:soumoditt@gmail.com)
