import subprocess
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parents[1]
CAPTURE_DIR = BASE_DIR / "captures"
CAPTURE_DIR.mkdir(exist_ok=True)


def capture_frame() -> Path:
    """Use rpicam-still to capture one JPEG and return its path."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = CAPTURE_DIR / f"raw_{ts}.jpg"

    result = subprocess.run(
        ["rpicam-still", "-n", "-t", "200", "-o", str(out_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"rpicam-still failed ({result.returncode}): "
            f"{result.stderr.decode(errors='ignore')}"
        )

    print(f"[OK] Captured frame: {out_path}")
    return out_path



def analyze_frame(path: Path) -> Path:
    """Basic OpenCV analysis: crop central ROI, find a dummy boundary, estimate fill%."""
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError(f"Failed to load image: {path}")

    h, w, _ = img.shape
    print(f"[INFO] Image size: {w}x{h}")

    # For now, central vertical slice as a fake "bin ROI"
    y0 = int(h * 0.2)
    y1 = int(h * 0.8)
    x0 = int(w * 0.4)
    x1 = int(w * 0.6)

    roi = img[y0:y1, x0:x1]
    roi_h, roi_w, _ = roi.shape
    print(f"[INFO] ROI size: {roi_w}x{roi_h} (x={x0}:{x1}, y={y0}:{y1})")

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Average brightness per row
    profile = gray.mean(axis=1)
    # Strongest change between rows as dummy "boundary"
    diff = np.abs(np.diff(profile))
    boundary_row = int(diff.argmax())

    print(f"[INFO] Boundary row (dummy): {boundary_row} / {roi_h}")

    # Treat bottom of ROI as 100%, top as 0%
    # Example: if boundary_row is near bottom -> low fill
    #          if boundary_row is near top   -> high fill
    pixels_from_bottom = roi_h - boundary_row
    fill_ratio = pixels_from_bottom / roi_h
    fill_percent = fill_ratio * 100.0
    print(f"[INFO] Estimated fill: {fill_percent:.1f}%")

    # Draw the candidate boundary in red on the ROI
    vis = roi.copy()
    cv2.line(
        vis,
        (0, boundary_row),
        (roi_w - 1, boundary_row),
        (0, 0, 255),
        2,
    )

    # Put text with fill% on the ROI
    cv2.putText(
        vis,
        f"{fill_percent:.1f}%",
        (5, max(20, boundary_row - 5)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    # Paste annotated ROI back into original image
    annotated = img.copy()
    annotated[y0:y1, x0:x1] = vis

    out_path = CAPTURE_DIR / f"debug_{path.stem}.jpg"
    cv2.imwrite(str(out_path), annotated)
    print(f"[OK] Saved annotated image: {out_path}")

    return out_path


def main() -> None:
    img_path = capture_frame()
    analyze_frame(img_path)


if __name__ == "__main__":
    main()
