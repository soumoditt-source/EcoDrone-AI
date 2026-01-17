import cv2
import numpy as np

def register_images(img1_bytes, img2_bytes):
    """
    Aligns img2 (OP3) to match img1 (OP1) using SIFT features.
    
    CRITICAL FIX: Preserves color channels throughout the pipeline.
    - Loads images in COLOR mode
    - Converts to grayscale ONLY for SIFT feature detection
    - Applies homography to the COLOR image
    
    Returns:
        The registered (warped) version of img2 in BGR color format.
    """
    # 1. Decode in COLOR mode (BGR)
    img1_color = cv2.imdecode(np.frombuffer(img1_bytes, np.uint8), cv2.IMREAD_COLOR)
    img2_color = cv2.imdecode(np.frombuffer(img2_bytes, np.uint8), cv2.IMREAD_COLOR)

    if img1_color is None or img2_color is None:
        print("[ERROR] Failed to decode images in color mode")
        return None

    # 2. Convert to grayscale for SIFT feature detection only
    img1_gray = cv2.cvtColor(img1_color, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2_color, cv2.COLOR_BGR2GRAY)

    # 3. SIFT Detector (Enhanced Feature Sensitivity)
    sift = cv2.SIFT_create(nfeatures=5000) # Increased for high-res drone maps
    kp1, des1 = sift.detectAndCompute(img1_gray, None)
    kp2, des2 = sift.detectAndCompute(img2_gray, None)

    if des1 is None or des2 is None:
        print("[ERROR] Failed to detect features in images")
        return None

    # 4. Match Features (FLANN based Matcher)
    # ---------------------------------------
    # We use a Fast Library for Approximate Nearest Neighbors to find
    # similar keypoints between Year 1 (OP1) and Year X (OP3).
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50) # Higher checks = more precision, slower
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    
    matches = flann.knnMatch(des1, des2, k=2)

    # 5. Filter Good Matches (Lowe's Ratio Test)
    # ------------------------------------------
    # Discard ambiguous matches. If the best match is not significantly
    # better than the 2nd best, it's noise.
    good = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)

    print(f"[INFO] Found {len(good)} good matches out of {len(matches)} total")

    if len(good) > 10:
        # We need at least 4 points for Homography, but 10 is safe.
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        # 6. Find Homography (RANSAC)
        # ---------------------------
        # Calculate the perspective transformation matrix that maps OP3 onto OP1.
        # RANSAC ignores outliers (bad matches).
        M, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
        
        if M is None:
            print("[ERROR] Failed to compute homography matrix")
            return None
        
        # 7. Warp COLOR img2 to match img1
        # CRITICAL: Apply transformation to the COLOR image, not grayscale
        h, w = img1_color.shape[:2]
        warped_img2_color = cv2.warpPerspective(img2_color, M, (w, h))
        
        print(f"[SUCCESS] Registration complete. Output shape: {warped_img2_color.shape}")
        return warped_img2_color
    else:
        print(f"[WARNING] Not enough matches found - {len(good)}/10. Skipping registration.")
        return None
