import cv2
import numpy as np
import os

def debug_omr(image_path, num_questions):
    print(f"Processing {image_path}")
    img = cv2.imread(image_path)
    if img is None:
        print("Error: Could not load image")
        return

    # Preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)
    
    cv2.imwrite("debug_thresh.png", thresh)

    # Find Contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    table_contour = None
    
    # Try to find a 4-point contour among the largest ones
    for c in contours[:5]:
        peri = cv2.arcLength(c, True)
        # Try different epsilons
        for eps in [0.02, 0.04, 0.06]:
            approx = cv2.approxPolyDP(c, eps * peri, True)
            if len(approx) == 4:
                table_contour = approx
                break
        if table_contour is not None:
            break
            
    if table_contour is None:
        # Fallback: Use the bounding box of the largest contour
        if len(contours) > 0:
            c = contours[0]
            x, y, w, h = cv2.boundingRect(c)
            # Create a 4-point contour from the bounding rect
            table_contour = np.array([[[x, y]], [[x+w, y]], [[x+w, y+h]], [[x, y+h]]])
            print("Using bounding box fallback")
        else:
            print("Table contour not found")
            return

    print("Table contour found.")
    
    # Perspective Transform
    pts = table_contour.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
        
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(gray, M, (maxWidth, maxHeight))
    warped_thresh = cv2.warpPerspective(thresh, M, (maxWidth, maxHeight))
    
    cv2.imwrite("debug_warped.png", warped)
    cv2.imwrite("debug_warped_thresh.png", warped_thresh)

    rows = num_questions + 1
    cols = 5
    
    cell_height = maxHeight // rows
    cell_width = maxWidth // cols
    
    print(f"Grid: {rows} rows, {cols} cols. Cell size: {cell_width}x{cell_height}")
    
    options = ['A', 'B', 'C', 'D']
    
    debug_grid = cv2.cvtColor(warped, cv2.COLOR_GRAY2BGR)
    
    for q_idx in range(1, rows):
        print(f"--- Question {q_idx} ---")
        best_col = -1
        max_pixels = 0
        
        for col_idx in range(1, 5):
            start_y = q_idx * cell_height
            end_y = (q_idx + 1) * cell_height
            start_x = col_idx * cell_width
            end_x = (col_idx + 1) * cell_width
            
            # Draw grid on debug image
            cv2.rectangle(debug_grid, (start_x, start_y), (end_x, end_y), (0, 0, 255), 1)
            
            margin = 5
            cell_roi = warped_thresh[start_y+margin:end_y-margin, start_x+margin:end_x-margin]
            
            non_zero = cv2.countNonZero(cell_roi)
            total_pixels = cell_roi.size
            ratio = non_zero / total_pixels if total_pixels > 0 else 0
            
            print(f"  Option {options[col_idx-1]}: Non-Zero={non_zero}, Total={total_pixels}, Ratio={ratio:.2f}")
            
            if non_zero > max_pixels:
                max_pixels = non_zero
                best_col = col_idx - 1
        
        if max_pixels > 40:
             print(f"  Detected: {options[best_col]}")
        else:
             print("  Detected: None")

    cv2.imwrite("debug_grid.png", debug_grid)

# Run with the uploaded image
image_path = "C:/Users/uach/.gemini/antigravity/brain/fca7ce03-96ea-4d32-95d7-f31dc49981e0/uploaded_image_1764782609177.png"
debug_omr(image_path, 2)
