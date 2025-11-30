import cv2

CAM_INDEX = 0          # change to 1 if needed
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

FLIP_VERTICAL = False   # set according to how the camera is mounted
FLIP_HORIZONTAL = False

def open_camera():
    cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_V4L2)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        raise RuntimeError("Cannot open USB camera")

    return cap


def read_frame(cap):
    ret, frame = cap.read()
    if not ret:
        raise RuntimeError("Failed to grab frame from USB camera")

    if FLIP_VERTICAL and FLIP_HORIZONTAL:
        frame = cv2.flip(frame, -1)
    elif FLIP_VERTICAL:
        frame = cv2.flip(frame, 0)
    elif FLIP_HORIZONTAL:
        frame = cv2.flip(frame, 1)

    return frame


def release_camera(cap):
    cap.release()
