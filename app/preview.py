import cv2
from camera import open_camera, read_frame, release_camera

def main():
    cap = open_camera()

    try:
        while True:
            frame = read_frame(cap)
            cv2.imshow("USB Cam Preview (q to quit)", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        release_camera(cap)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
