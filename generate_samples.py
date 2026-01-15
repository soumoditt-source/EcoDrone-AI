import cv2
import numpy as np
import os
import random

def create_sample_images():
    # 1. Setup Canvas (1000x1000 represents a small patch)
    height, width = 1000, 1000
    
    # --- OP1: Soil with Pits (Brownish) ---
    op1_img = np.zeros((height, width, 3), dtype=np.uint8)
    op1_img[:] = (60, 90, 120)  # BGR: Brownish soil color
    
    # Add Texture (Noise)
    noise = np.random.randint(0, 30, (height, width, 3), dtype=np.uint8)
    op1_img = cv2.add(op1_img, noise)

    # Define Pit Locations (Grid)
    pits = []
    rows, cols = 5, 5
    spacing_x = width // (cols + 1)
    spacing_y = height // (rows + 1)
    
    for i in range(rows):
        for j in range(cols):
            x = (j + 1) * spacing_x + random.randint(-10, 10) # Slight random jitter
            y = (i + 1) * spacing_y + random.randint(-10, 10)
            pits.append((x, y))
            
            # Draw Pit (Darker circle)
            cv2.circle(op1_img, (x, y), 20, (30, 50, 80), -1) # 20px radius ~ 45cm
            # Add "shadow" or edge to pit
            cv2.circle(op1_img, (x, y), 20, (20, 40, 60), 2)

    # Save OP1
    cv2.imwrite("sample_op1.png", op1_img)
    print("Created sample_op1.png")

    # --- OP3: Soil + Saplings (Green) ---
    op3_img = op1_img.copy()
    
    # Simulate slightly different lighting/shift (Registration challenge)
    M = np.float32([[1, 0, 5], [0, 1, 5]]) # 5px shift
    op3_img = cv2.warpAffine(op3_img, M, (width, height))
    
    # Planting: 80% Survival
    for idx, (px, py) in enumerate(pits):
        # Shift pit coords slightly for drawing because we shifted the image
        px += 5
        py += 5
        
        if random.random() > 0.2: # 80% chance alive
            # Draw Plant (Green varietes)
            color = (50, random.randint(180, 255), 50) # Bright Green
            radius = random.randint(15, 25)
            cv2.circle(op3_img, (px, py), radius, color, -1)
            # Add some "leaves" texture
            cv2.circle(op3_img, (px+5, py+5), 10, (40, 200, 40), -1)
            cv2.circle(op3_img, (px-5, py-5), 8, (60, 220, 60), -1)
        else:
            # Dead/Empty (Maybe just weeds or nothing)
            # Draw small weeds (yellowish/dull green)
            if random.random() > 0.5:
                 cv2.circle(op3_img, (px, py), 10, (50, 100, 100), -1) # Dry grass

    # Save OP3
    cv2.imwrite("sample_op3.png", op3_img)
    print("Created sample_op3.png")

if __name__ == "__main__":
    create_sample_images()
