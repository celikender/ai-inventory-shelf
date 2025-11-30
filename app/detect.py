import cv2
import numpy as np
from camera import open_camera, read_frame, release_camera

# ---------- TUNING ----------

MIN_AREA_ITEM = 1000        # bigger -> less sensitive, smaller -> more sensitive
INVERT_ITEMS = False       # items are brighter than background
BOX_INSET = 5              # crop a bit inside the green frame

GRID_ROWS = 10
GRID_COLS = 10

# ----------------------------


def find_green_box(frame):
    """Detect the main green square and return (x, y, w, h), mask."""
    blur = cv2.GaussianBlur(frame, (5, 5), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    lower_green = (35, 40, 40)
    upper_green = (85, 255, 255)
    mask = cv2.inRange(hsv, lower_green, upper_green)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, mask

    c = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)
    return (x, y, w, h), mask


def detect_items_and_grid(roi):
    """Item detection + grid drawing inside ROI. Returns roi_with_drawings, num_items."""
    h, w = roi.shape[:2]
    roi_area = w * h
    cell_w = w / GRID_COLS
    cell_h = h / GRID_ROWS

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    _, mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if INVERT_ITEMS:
        mask = 255 - mask

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # thresholds relative to cell size
    min_area = max(MIN_AREA_ITEM, int(0.15 * cell_w * cell_h))
    min_dim = int(0.25 * min(cell_w, cell_h))

    detections = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < min_area:
            continue

        x, y, w_box, h_box = cv2.boundingRect(c)

        # ignore tiny/thin blobs (noise)
        if w_box < min_dim and h_box < min_dim:
            continue

        # ignore something that covers most of ROI (plate itself)
        if area > 0.5 * roi_area:
            continue

        detections.append(c)

    # draw detections
    for c in detections:
        x, y, w_box, h_box = cv2.boundingRect(c)
        cv2.rectangle(roi, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)

    # draw 10x10 grid lines for visualization only
    for c in range(1, GRID_COLS):
        x = int(c * cell_w)
        cv2.line(roi, (x, 0), (x, h), (0, 255, 255), 1)

    for r in range(1, GRID_ROWS):
        y = int(r * cell_h)
        cv2.line(roi, (0, y), (w, y), (0, 255, 255), 1)

    num_items = len(detections)

    cv2.putText(
        roi,
        f"Items: {num_items}",
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2,
    )

    return roi, mask, num_items


def main():
    cap = open_camera()

    try:
        while True:
            frame = read_frame(cap)

            box, green_mask = find_green_box(frame)

            if box is not None:
                x, y, w, h = box
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)

                x_in = x + BOX_INSET
                y_in = y + BOX_INSET
                w_in = max(1, w - 2 * BOX_INSET)
                h_in = max(1, h - 2 * BOX_INSET)

                roi = frame[y_in:y_in + h_in, x_in:x_in + w_in].copy()

                roi_vis, item_mask, num_items = detect_items_and_grid(roi)

                cv2.imshow("ROI grid", roi_vis)
                cv2.imshow("Item mask", item_mask)
            else:
                cv2.putText(
                    frame,
                    "No green box found",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow("Full frame", frame)
            cv2.imshow("Green mask", green_mask)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        release_camera(cap)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
