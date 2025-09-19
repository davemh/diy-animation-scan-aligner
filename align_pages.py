#!/usr/bin/env python3
import cv2
import numpy as np
import os
from tqdm import tqdm

# ---------------- Hole Detection ---------------- #
def detect_three_holes(image):
    """Detects 3 circular holes in the scan. Returns centers as list of (x,y)."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 2)
    circles = cv2.HoughCircles(
        blur,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=200,
        param1=50,
        param2=30,
        minRadius=20,
        maxRadius=80
    )
    if circles is None or len(circles[0]) < 3:
        raise RuntimeError("Could not detect punch holes on the page")
    circles = np.round(circles[0, :]).astype("int")
    # sort left to right
    circles = sorted(circles, key=lambda c: c[0])
    return [(c[0], c[1]) for c in circles[:3]]

# ---------------- Reference Builder ---------------- #
def build_reference(holes, img_shape, holes_position="top"):
    """Rotate holes so they are horizontal, return as reference positions."""
    (h, w) = img_shape[:2]
    holes = np.array(holes, dtype=np.float32)

    dx = holes[2][0] - holes[0][0]
    dy = holes[2][1] - holes[0][1]
    angle = np.degrees(np.arctan2(dy, dx))
    rot_mat = cv2.getRotationMatrix2D(tuple(holes[1]), -angle, 1.0)
    rotated = cv2.transform(np.array([holes]), rot_mat)[0]

    if holes_position == "top":
        target_y = int(0.1 * h)
    else:
        target_y = int(0.9 * h)
    y_offset = target_y - np.mean(rotated[:, 1])
    rotated[:, 1] += y_offset

    return rotated

# ---------------- Alignment ---------------- #
def align_page(image, detected, reference):
    """Align one page to reference using rigid affine transform."""
    src = np.array(detected, dtype=np.float32)
    dst = np.array(reference, dtype=np.float32)

    M, _ = cv2.estimateAffinePartial2D(src, dst, method=cv2.LMEDS)
    if M is None:
        raise RuntimeError("Failed to compute alignment transform")

    aligned = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]),
                             flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

    return aligned

# ---------------- Main Processing ---------------- #
def process_folder(input_dir, output_dir, holes_position="top", debug=False, preview=False, preview_delay=500):
    files = sorted([f for f in os.listdir(input_dir)
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff'))])
    if not files:
        print("No images found in input folder")
        return

    os.makedirs(output_dir, exist_ok=True)
    reference = None

    for fname in tqdm(files, desc="Processing pages"):
        in_path = os.path.join(input_dir, fname)
        img = cv2.imread(in_path)
        if img is None:
            print(f"Warning: failed to read {fname}")
            continue

        try:
            holes = detect_three_holes(img)
        except RuntimeError as e:
            print(f"Skipping {fname}: {e}")
            continue

        if reference is None:
            reference = build_reference(holes, img.shape, holes_position)

        try:
            aligned = align_page(img, holes, reference)
        except RuntimeError as e:
            print(f"Skipping {fname}: {e}")
            continue

        out_name = os.path.splitext(fname)[0] + ".png"
        cv2.imwrite(os.path.join(output_dir, out_name), aligned)

        if preview:
            disp = aligned.copy()
            cv2.putText(disp, fname, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 4)
            cv2.putText(disp, fname, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
            cv2.imshow("Preview", disp)
            key = cv2.waitKey(preview_delay) & 0xFF
            if key == 27:  # ESC
                break

    if preview:
        cv2.destroyAllWindows()
