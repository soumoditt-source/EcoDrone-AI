import cv2
import numpy as np

def detect_pits(image_bytes: bytes, gsd_cm_px: float = 2.5):
    """
    Detects planting pits using Hough Circle Transform.
    
    Args:
        image_bytes: Raw image data.
        gsd_cm_px: Ground Sampling Distance (cm/pixel). Default 2.5cm/px from problem statement.
        
    Returns:
        List of (x, y, r) tuples.
    """
    # 1. Decode image
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        return []

    # 2. Convert to Grayscale & Blur
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Median blur to remove salt-and-pepper noise from soil texture
    gray_blurred = cv2.medianBlur(gray, 5)

    # 3. Calculate Radius in Pixels
    # Pit size = 45cm diameter -> 22.5cm radius
    # Pixels = 22.5 / 2.5 = 9 pixels
    target_radius = int(22.5 / gsd_cm_px)
    min_radius = int(target_radius * 0.8)  # Allow 20% variance
    max_radius = int(target_radius * 1.2)

    # 4. Hough Circle Transform (Field-Tuned for Real Noise)
    # -----------------------------------------------------------------
    # Param1 (Edge sensitivity) lowered to 40 for broader feature detection.
    # Param2 (Center accuracy) set to 35 to reject false positives from soil clumps.
    # minDist increased to 0.7x spacing to force separation of adjacent pits.
    min_dist = int(250 / gsd_cm_px * 0.7) 
    
    circles = cv2.HoughCircles(
        gray_blurred, 
        cv2.HOUGH_GRADIENT, 
        dp=1.2, 
        minDist=min_dist,
        param1=40, 
        param2=35, 
        minRadius=min_radius, 
        maxRadius=max_radius
    )

    detected_pits = []
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            detected_pits.append({"x": int(x), "y": int(y), "r": int(r)})
            
    return detected_pits
