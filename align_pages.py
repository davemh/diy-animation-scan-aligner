import cv2
import numpy as np
import os
import sys


def detect_punch_holes(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Blur and threshold
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    holes = []
    for c in contours:
        area = cv2.contourArea(c)
        if 50 < area < 5000:  # reasonable size range for punch holes
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                holes.append((cx, cy))

    if len(holes) < 2:
        raise ValueError("Could not detect punch holes")

    # Sort holes by y coordinate (top and bottom)
    holes = sorted(holes, key=lambda x: x[1])
    top_hole, bottom_hole = holes[0], holes[-1]

    return {"top": top_hole, "bottom": bottom_hole}


def align_image(image_path, ref_holes, output_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    detected = detect_punch_holes(image_path)

    src_points = np.float32([detected["top"], detected["bottom"]])
    dst_points = np.float32([ref_holes["top"], ref_holes["bottom"]])

    # Calculate affine transform
    matrix = cv2.getAffineTransform(
        np.vstack([src_points, [src_points[1][0] + 1, src_points[1][1]]]),
        np.vstack([dst_points, [dst_points[1][0] + 1, dst_points[1][1]]])
    )

    aligned = cv2.warpAffine(image, matrix, (image.shape[1], image.shape[0]))
    cv2.imwrite(output_path, aligned)


def process_folder(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = [f for f in os.listdir(input_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    if not files:
        raise ValueError("No image files found in input directory")

    ref_image = os.path.join(input_dir, files[0])
    ref_holes = detect_punch_holes(ref_image)

    for f in files:
        in_path = os.path.join(input_dir, f)
        out_path = os.path.join(output_dir, f)
        align_image(in_path, ref_holes, out_path)
        print(f"Aligned {f}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python align_pages.py <input_dir> <output_dir>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    try:
        process_folder(input_dir, output_dir)
        print("All images aligned successfully.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
