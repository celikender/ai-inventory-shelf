import cv2

cam_index = 0  # try 0, if fail try 1

cap = cv2.VideoCapture(cam_index, cv2.CAP_V4L2)

if not cap.isOpened():
    print("Cannot open camera", cam_index)
    exit(1)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow("Test camera", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break

cap.release()
cv2.destroyAllWindows()
