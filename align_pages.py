import cv2
import numpy as np
import os
import argparse


def align_page(src_path, dst_path, holes_position="top", debug=False, preview=False):
    """
    Align a single scanned animation page based on punch holes.
    """

    # Load image
    img = cv2.imread(src_path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {src_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Find contours (holes should be dark regions)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by area (largest first)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Expect at least 2-3 holes
    hole_centers = []
    for cnt in contours[:5]:
        (x, y, w, h) = cv2.boundingRect(cnt)
        if w < 50 and h < 50:  # ignore large blobs
            M = cv2.moments(cnt)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                hole_centers.append((cx, cy))

    if len(hole_centers) < 2:
        raise RuntimeError("Could not detect enough punch holes.")

    # Sort holes left-to-right or top-to-bottom
    if holes_position == "top":
        hole_centers = sorted(hole_centers, key=lambda c: c[0])  # sort by x
    else:
        hole_centers = sorted(hole_centers, key=lambda c: c[1])  # sort by y

    # Define reference positions (peg bar positions)
    ref_distance = 1000  # arbitrary scale
    if holes_position == "top":
        ref_pts = np.float32([[0, 0], [ref_distance, 0]])
    else:
        ref_pts = np.float32([[0, 0], [0, ref_distance]])

    # Use first two detected holes
    src_pts = np.float32(hole_centers[:2])

    # Compute affine transform
    matrix = cv2.getAffineTransform(
        np.vstack([src_pts, [src_pts[1][0], src_pts[1][1] + 1]]),
        np.vstack([ref_pts, [ref_pts[1][0], ref_pts[1][1] + 1]]),
    )

    aligned = cv2.warpAffine(
        img, matrix, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR
    )

    if preview or debug:
        cv2.imshow("Aligned", aligned)
        cv2.waitKey(500)

    cv2.imwrite(dst_path, aligned)


def process_folder(
    src, dst, holes_position="top", debug=False, preview=False, progress_callback=None
):
    """
    Align all scanned frames in a folder.
    """
    files = sorted(
        f
        for f in os.listdir(src)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff"))
    )

    total = len(files)
    if total == 0:
        return

    os.makedirs(dst, exist_ok=True)

    for i, fname in enumerate(files, 1):
        src_path = os.path.join(src, fname)
        dst_path = os.path.join(dst, fname)

        align_page(
            src_path, dst_path, holes_position=holes_position, debug=debug, preview=preview
        )

        if progress_callback:
            progress_callback(i, total, fname)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Align scanned animation pages.")
    parser.add_argument("src", help="Source folder")
    parser.add_argument("dst", help="Destination folder")
    parser.add_argument("--holes", choices=["top", "left"], default="top")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()

    process_folder(
        args.src,
        args.dst,
        holes_position=args.holes,
        debug=args.debug,
        preview=args.preview,
    )
