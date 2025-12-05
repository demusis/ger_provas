import cv2
import numpy as np

def process_exam_image(image_path, num_questions):
    """
    Process the exam image to identify marked answers.
    
    Args:
        image_path (str): Path to the image file.
        num_questions (int): Number of questions in the exam.
        
    Returns:
        dict: A dictionary mapping question number (int) to detected answer ('A', 'B', 'C', 'D').
    """
    # 1. Load Image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not load image")

    # 2. Preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # 3. Find Contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort contours by area, largest first
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
            return {}

    # 4. Perspective Transform (Warp)
    # Order points: top-left, top-right, bottom-right, bottom-left
    pts = table_contour.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    (tl, tr, br, bl) = rect
    
    # Compute width of new image
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    
    # Compute height of new image
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

    # 5. Split into cells
    # The table has (num_questions + 1) rows (header + questions)
    # And 5 columns (Q, A, B, C, D)
    
    rows = num_questions + 1
    cols = 5
    
    cell_height = maxHeight // rows
    cell_width = maxWidth // cols
    
    detected_answers = {}
    
    # We skip the first row (header)
    for q_idx in range(1, rows):
        # Question number is q_idx
        
        # We check columns 1, 2, 3, 4 (A, B, C, D) - 0-indexed
        # Column 0 is the question number
        
        best_col = -1
        max_pixels = 0
        
        # Threshold for considering a bubble filled
        # This might need tuning
        
        options = ['A', 'B', 'C', 'D']
        pixel_counts = []
        
        for col_idx in range(1, 5):
            # Extract cell ROI
            start_y = q_idx * cell_height
            end_y = (q_idx + 1) * cell_height
            start_x = col_idx * cell_width
            end_x = (col_idx + 1) * cell_width
            
            # Use the thresholded warped image to count white pixels (which correspond to dark marks in original)
            # Note: In our thresh (BINARY_INV), dark marks became white.
            # However, we might want to be careful about borders.
            # Let's crop the cell slightly to avoid borders
            margin = 5
            cell_roi = warped_thresh[start_y+margin:end_y-margin, start_x+margin:end_x-margin]
            
            non_zero = cv2.countNonZero(cell_roi)
            pixel_counts.append(non_zero)
            
            if non_zero > max_pixels:
                max_pixels = non_zero
                best_col = col_idx - 1 # 0 for A, 1 for B...
        
        # Heuristic: The filled bubble should have significantly more pixels than empty ones
        # For now, we just take the max, but in a real system we'd check if it exceeds a threshold
        # relative to the cell area or relative to other options.
        
        # Simple check: if max_pixels is very low, maybe nothing is marked
        if max_pixels > 40: # Lowered threshold based on debug results
             detected_answers[q_idx] = options[best_col]
             
    return detected_answers
